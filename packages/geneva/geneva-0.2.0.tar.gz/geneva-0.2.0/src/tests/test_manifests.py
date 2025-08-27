# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import copy
from pathlib import Path
from unittest.mock import MagicMock

from geneva import connect
from geneva.manifest.mgr import GenevaManifest


def test_manifest_crud(tmp_path: Path) -> None:
    mock_uploader = MagicMock()
    mock_uploader.upload_dir = "/mock/upload/dir"
    mock_uploader._file_exists.return_value = False
    mock_uploader.upload.side_effect = lambda path: f"mock://{path.name}"

    geneva = connect(tmp_path)

    manifest_def = GenevaManifest(
        name="test-manifest-1",
        local_zip_output_dir=str(tmp_path),
        skip_site_packages=False,
        delete_local_zips=False,
        pip=["numpy", "pandas"],
        py_modules=["pyarrow"],
    )

    # upload and create
    geneva.define_manifest("test-manifest-1", manifest_def, uploader=mock_uploader)
    m = geneva.list_manifests()[0]
    _assert_manifest_eq(m.as_dict(), manifest_def.as_dict())

    upload_count = mock_uploader.upload.call_count
    assert upload_count >= 1, "files were not uploaded"

    # update - should update metadata and upload new artifacts
    manifest_def.skip_site_packages = True
    geneva.define_manifest("test-manifest-1", manifest_def, uploader=mock_uploader)
    manifests = geneva.list_manifests()
    assert len(manifests) == 1, "expected single manifest"
    m1 = manifests[0].as_dict()
    m2 = manifest_def.as_dict()
    assert m1["checksum"] != m2["checksum"], "checksum should change"
    _assert_manifest_eq(m1, m2)
    assert mock_uploader.upload.call_count >= upload_count, "files were not uploaded"

    # delete
    geneva.delete_manifest("test-manifest-1")
    assert geneva.list_manifests() == []


def _assert_manifest_eq(m1: dict, m2: dict) -> bool:
    m1 = copy.deepcopy(m1)
    m2 = copy.deepcopy(m2)
    # exclude transient fields from comparison
    for f in {"checksum", "zips"}:
        if f in m1:
            del m1[f]
        if f in m2:
            del m2[f]
    assert m1 == m2, "manifests should match"
