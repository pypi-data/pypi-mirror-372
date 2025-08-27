# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors
import enum
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import attrs
import cattrs

from geneva.utils import current_user
from geneva.utils.arrow import schema_from_attrs

MANIFEST_TABLE_NAME = "geneva_manifests"

_LOG = logging.getLogger(__name__)


@attrs.define
class GenevaManifest:
    """A Geneva Manifest represents the files and dependencies used
    in the execution environment."""

    # metadata
    name: str = attrs.field()
    version: Optional[str] = attrs.field(default=None)

    # properties needed to init the cluster
    pip: list[str] = attrs.field(default=[])
    py_modules: list[str] = attrs.field(default=[])

    # transient properties, only used during initial upload
    skip_site_packages: bool = attrs.field(default=False)
    delete_local_zips: bool = attrs.field(default=False)
    local_zip_output_dir: Optional[str] = attrs.field(default=None)

    # internal generated properties
    zips: list[list[str]] = attrs.field(default=[[]])
    checksum: Optional[str] = attrs.field(default=None)
    created_at: datetime = attrs.field()
    created_by: str = attrs.field()

    def __attrs_post_init__(self) -> None:
        self.checksum = self.compute_checksum()

    @created_at.default
    def _default_created_at(self) -> datetime:
        return datetime.now(timezone.utc)

    @created_by.default
    def _default_created_by(self) -> str:
        return current_user()

    def compute_checksum(self) -> str:
        """Generate a stable checksum of the manifest, ignoring the checksum field.
        The zip file names include the checksum of the contents so this hash is
        comprehensive.
        """
        checksum_exclude_fields = {
            "checksum",
            "created_at",
            "created_by",
            "delete_local_zips",
            "local_zip_output_dir",
        }
        data = attrs.asdict(
            self,
            recurse=True,
            filter=lambda a, v: a.name not in checksum_exclude_fields,
        )
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict:
        return attrs.asdict(
            self,
            value_serializer=lambda obj, a, v: v.value
            if isinstance(v, enum.Enum)
            else v,
        )


class ManifestConfigManager:
    from geneva.db import Connection

    def __init__(
        self, genevadb: Connection, manifest_table_name=MANIFEST_TABLE_NAME
    ) -> None:
        self.db = genevadb
        try:
            self.manifest_table = self.db.open_table(manifest_table_name)
        except ValueError:
            self.manifest_table = self.db.create_table(
                manifest_table_name,
                schema=schema_from_attrs(GenevaManifest),
            )

    def upsert(self, manifest: GenevaManifest) -> None:
        val = manifest.as_dict()
        self.delete(manifest.name)
        self.manifest_table.add([val])
        # # note: merge_insert with fails with schema errors - use delete+add for now
        # todo: fix schema error on merge_insert?

    def list(self, limit: int = 1000) -> list[GenevaManifest]:
        res = self.manifest_table._ltbl.search().limit(limit).to_arrow().to_pylist()
        return [_make_manifest(manifest) for manifest in res]

    def load(self, name: str) -> GenevaManifest | None:
        res = (
            self.manifest_table._ltbl.search()
            .where(f"name = '{name}'")
            .limit(1)
            .to_arrow()
            .to_pylist()
        )
        if not res:
            return None
        return _make_manifest(res[0])

    def delete(self, name: str) -> None:
        self.manifest_table._ltbl.delete(f"name = '{name}'")


def _make_manifest(args: dict) -> GenevaManifest:
    converter = cattrs.Converter()
    converter.register_structure_hook(
        datetime,
        lambda ts, _: datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if isinstance(ts, str)
        else ts,
    )
    res = converter.structure(args, GenevaManifest)

    return res
