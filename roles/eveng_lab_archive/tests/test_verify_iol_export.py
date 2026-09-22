from __future__ import annotations

import base64
import importlib.util
import io
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree


SCRIPT = Path(__file__).resolve().parents[1] / "files" / "verify_iol_export.py"
SPEC = importlib.util.spec_from_file_location("verify_iol_export", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
LAB_ID = "11111111-1111-4111-8111-111111111111"


class VerifyIolExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lab = self.root / "lab.unl"
        self.state = self.root / "tmp"
        self.state.mkdir()

    def write_lab(self, iol_count: int, vpcs_count: int, configs: set[int]) -> None:
        root = ElementTree.Element("lab", {"id": LAB_ID})
        nodes = ElementTree.SubElement(ElementTree.SubElement(root, "topology"), "nodes")
        for node_id in range(1, iol_count + 1):
            ElementTree.SubElement(
                nodes, "node", {"id": str(node_id), "name": f"IOL-{node_id}", "type": "iol"}
            )
        for node_id in range(iol_count + 1, iol_count + vpcs_count + 1):
            ElementTree.SubElement(
                nodes, "node", {"id": str(node_id), "name": f"PC-{node_id}", "type": "vpcs"}
            )
        saved = ElementTree.SubElement(ElementTree.SubElement(root, "objects"), "configs")
        for node_id in sorted(configs):
            config = ElementTree.SubElement(saved, "config", {"id": str(node_id)})
            config.text = base64.b64encode(f"hostname IOL-{node_id}\n".encode()).decode()
        ElementTree.ElementTree(root).write(self.lab, encoding="utf-8")

    def write_nvram(self, *node_ids: int) -> None:
        for node_id in node_ids:
            node_dir = self.state / "0" / LAB_ID / str(node_id)
            node_dir.mkdir(parents=True)
            (node_dir / f"nvram_{node_id << 4:05d}").write_bytes(b"saved device state")

    def test_missing_configured_iol_nodes_fail_as_a_group(self) -> None:
        self.write_lab(7, 4, {8, 9, 10, 11})
        self.write_nvram(1, 2, 3, 7)
        with self.assertRaisesRegex(ValueError, "IOL-1 \\(id 1\\).*, IOL-7 \\(id 7\\)"):
            MODULE.verify(self.lab, self.state)

    def test_configured_iol_nodes_pass_with_unconfigured_peers(self) -> None:
        self.write_lab(7, 4, {1, 2, 3, 7, 8, 9, 10, 11})
        self.write_nvram(1, 2, 3, 7)
        self.assertEqual(MODULE.verify(self.lab, self.state), (4, 7))

    def test_multiple_iol_and_vpcs_configs_pass(self) -> None:
        self.write_lab(11, 5, set(range(1, 17)))
        self.write_nvram(*range(1, 12))
        self.assertEqual(MODULE.verify(self.lab, self.state), (11, 11))

    def test_unconfigured_iol_nodes_without_nvram_pass(self) -> None:
        self.write_lab(3, 2, set())
        self.assertEqual(MODULE.verify(self.lab, self.state), (0, 3))

    def test_lab_without_iol_does_not_require_a_lab_id(self) -> None:
        self.lab.write_text('<lab name="routing"/>')
        self.assertEqual(MODULE.verify(self.lab, self.state), (0, 0))

    def test_empty_nvram_is_not_accepted(self) -> None:
        self.write_lab(1, 0, {1})
        self.write_nvram(1)
        next(self.state.glob("**/nvram_*")).write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "empty NVRAM"):
            MODULE.verify(self.lab, self.state)

    def test_invalid_embedded_config_is_not_accepted(self) -> None:
        self.write_lab(1, 0, {1})
        self.write_nvram(1)
        tree = ElementTree.parse(self.lab)
        tree.find("./objects/configs/config").text = "not-base64"
        tree.write(self.lab)
        with self.assertRaisesRegex(ValueError, "IOL-1 \\(id 1\\)"):
            MODULE.verify(self.lab, self.state)

    def test_started_node_without_nvram_fails(self) -> None:
        self.write_lab(1, 0, set())
        (self.state / "0" / LAB_ID / "1").mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "NVRAM missing"):
            MODULE.verify(self.lab, self.state)

    def test_stopped_iol_config_is_sent_through_eve_api(self) -> None:
        self.write_lab(1, 0, set())
        self.write_nvram(1)
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = io.BytesIO(
            b'{"code":201,"status":"success"}'
        )
        export = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"hostname IOL-1\n", stderr=b""
        )
        with patch.object(MODULE, "build_opener", return_value=opener), patch.object(
            MODULE.subprocess, "run", return_value=export
        ) as run:
            recovered = MODULE.recover(
                self.lab,
                self.state,
                api_base_url="http://127.0.0.1",
                api_lab="student/routing lab.unl",
                cookie="PHPSESSID=test",
                iou_export=Path("/opt/unetlab/scripts/iou_export"),
                timeout=30,
                validate_certs=True,
            )

        self.assertEqual(recovered, 1)
        self.assertEqual(run.call_args.args[0][-1], "/dev/stdout")
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), "PUT")
        self.assertEqual(
            request.full_url,
            "http://127.0.0.1/api/labs/student/routing%20lab.unl/configs/1",
        )
        self.assertEqual(json.loads(request.data), {"data": "hostname IOL-1\n"})

    def test_recovery_does_not_replace_existing_config(self) -> None:
        self.write_lab(1, 0, {1})
        self.write_nvram(1)
        with patch.object(MODULE.subprocess, "run") as run:
            recovered = MODULE.recover(
                self.lab,
                self.state,
                api_base_url="http://127.0.0.1",
                api_lab="lab.unl",
                cookie="PHPSESSID=test",
                iou_export=Path("/opt/unetlab/scripts/iou_export"),
                timeout=30,
                validate_certs=True,
            )
        self.assertEqual(recovered, 0)
        run.assert_not_called()

    def test_recovery_fails_when_saved_nvram_cannot_be_exported(self) -> None:
        self.write_lab(1, 0, set())
        self.write_nvram(1)
        export = subprocess.CompletedProcess(
            args=[], returncode=1, stdout=b"", stderr=b"invalid NVRAM"
        )
        with patch.object(MODULE.subprocess, "run", return_value=export), patch.object(
            MODULE, "build_opener"
        ) as opener:
            with self.assertRaisesRegex(ValueError, "saved NVRAM could not be exported"):
                MODULE.recover(
                    self.lab,
                    self.state,
                    api_base_url="http://127.0.0.1",
                    api_lab="lab.unl",
                    cookie="PHPSESSID=test",
                    iou_export=Path("/opt/unetlab/scripts/iou_export"),
                    timeout=30,
                    validate_certs=True,
                )
        opener.return_value.open.assert_not_called()

    def test_recovery_fails_when_eve_rejects_config(self) -> None:
        self.write_lab(1, 0, set())
        self.write_nvram(1)
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = io.BytesIO(
            b'{"status":"fail","message":"update failed"}'
        )
        export = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"hostname IOL-1\n", stderr=b""
        )
        with patch.object(MODULE, "build_opener", return_value=opener), patch.object(
            MODULE.subprocess, "run", return_value=export
        ):
            with self.assertRaisesRegex(ValueError, "EVE-NG config API rejected"):
                MODULE.recover(
                    self.lab,
                    self.state,
                    api_base_url="http://127.0.0.1",
                    api_lab="lab.unl",
                    cookie="PHPSESSID=test",
                    iou_export=Path("/opt/unetlab/scripts/iou_export"),
                    timeout=30,
                    validate_certs=True,
                )


if __name__ == "__main__":
    unittest.main()
