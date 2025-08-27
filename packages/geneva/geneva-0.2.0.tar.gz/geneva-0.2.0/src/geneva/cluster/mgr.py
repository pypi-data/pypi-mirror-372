# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors
import enum
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import attrs
import cattrs
from attr import asdict

from geneva.cluster import GenevaClusterType, K8sConfigMethod
from geneva.utils import current_user
from geneva.utils.arrow import schema_from_attrs

CLUSTER_TABLE_NAME = "geneva_clusters"

_LOG = logging.getLogger(__name__)


@attrs.define
class RayGroupConfig:
    """Configuration for Ray pods"""

    service_account: str = attrs.field()
    num_cpus: int = attrs.field()
    memory: str = attrs.field()
    image: str = attrs.field()

    # store these as json strings
    node_selector: dict[str, str] = attrs.field(metadata={"pa_type": "string"})
    labels: dict[str, str] = attrs.field(metadata={"pa_type": "string"})
    tolerations: list[dict[str, str]] = attrs.field(metadata={"pa_type": "string"})

    num_gpus: int = attrs.field(default=0)


@attrs.define
class HeadGroupConfig(RayGroupConfig):
    """Configuration for Ray Head pod"""


@attrs.define
class WorkerGroupConfig(RayGroupConfig):
    """Configuration for Ray Worker pods"""


# todo: make config map impl use this model
@attrs.define
class KubeRayConfig:
    namespace: str = attrs.field()
    head_group: HeadGroupConfig = attrs.field()
    # todo: lance bug prevents us from storing list<struct>
    #  - store as json string for now
    worker_groups: list[WorkerGroupConfig] = attrs.field(metadata={"pa_type": "string"})
    config_method: K8sConfigMethod = attrs.field(default=K8sConfigMethod.LOCAL)
    use_portforwarding: bool = attrs.field(default=True)
    aws_region: Optional[str] = attrs.field(default=None)
    aws_role_name: Optional[str] = attrs.field(default=None)


@attrs.define
class GenevaCluster:
    """A Geneva Cluster represents the backend compute infrastructure
    for the execution environment."""

    cluster_type: GenevaClusterType = attrs.field()
    name: str = attrs.field()
    kuberay: Optional[KubeRayConfig] = attrs.field(default=None)
    created_at: datetime = attrs.field()
    created_by: str = attrs.field()

    @created_at.default
    def _default_created_at(self) -> datetime:
        return datetime.now(timezone.utc)

    @created_by.default
    def _default_created_by(self) -> str:
        return current_user()

    def to_ray_cluster(self) -> "RayCluster":  # noqa: F821
        """Convert the persisted cluster definition into internal RayCluster model"""
        from geneva.runners.ray.raycluster import (
            RayCluster,
            _HeadGroupSpec,
            _WorkerGroupSpec,
        )

        c = asdict(self)
        k = c["kuberay"]
        k.pop("use_portforwarding")
        k["region"] = k.pop("aws_region")
        k["role_name"] = k.pop("aws_role_name")
        k["name"] = c["name"]
        k["config_method"] = K8sConfigMethod(k["config_method"])
        k["head_group"] = _HeadGroupSpec(**k["head_group"])
        k["worker_groups"] = [_WorkerGroupSpec(**wg) for wg in k["worker_groups"]]
        rc = RayCluster(**k)
        return rc

    def as_dict(self) -> dict:
        return attrs.asdict(
            self,
            value_serializer=lambda obj, a, v: v.value
            if isinstance(v, enum.Enum)
            else v,
        )


class ClusterConfigManager:
    from geneva.db import Connection

    def __init__(
        self, genevadb: Connection, cluster_table_name=CLUSTER_TABLE_NAME
    ) -> None:
        self.db = genevadb
        try:
            self.cluster_table = self.db.open_table(cluster_table_name)
        except ValueError:
            self.cluster_table = self.db.create_table(
                cluster_table_name,
                schema=schema_from_attrs(GenevaCluster),
            )

    def upsert(self, cluster: GenevaCluster) -> None:
        val = cluster.as_dict()
        # store list<struct> as json string for now due to lance bug
        val["kuberay"]["worker_groups"] = json.dumps(val["kuberay"]["worker_groups"])

        # store maps as json strings
        hg = val["kuberay"]["head_group"]
        hg["node_selector"] = json.dumps(hg["node_selector"])
        hg["tolerations"] = json.dumps(hg["tolerations"])
        hg["labels"] = json.dumps(hg["labels"])

        # note: merge_insert with fails with schema errors - use delete+add for now
        self.delete(cluster.name)
        self.cluster_table.add([val])

    def list(self, limit: int = 1000) -> list[GenevaCluster]:
        res = self.cluster_table._ltbl.search().limit(limit).to_arrow().to_pylist()
        return [_make_cluster(cluster) for cluster in res]

    def load(self, name: str) -> GenevaCluster | None:
        res = (
            self.cluster_table._ltbl.search()
            .where(f"name = '{name}'")
            .limit(1)
            .to_arrow()
            .to_pylist()
        )
        if not res:
            return None
        return _make_cluster(res[0])

    def delete(self, name: str) -> None:
        self.cluster_table._ltbl.delete(f"name = '{name}'")


def _make_cluster(args: dict) -> GenevaCluster:
    # parse stringified json fields
    kr = args["kuberay"]
    kr["worker_groups"] = json.loads(kr["worker_groups"])
    hg = kr["head_group"]
    hg["node_selector"] = json.loads(hg["node_selector"])
    hg["labels"] = json.loads(hg["labels"])
    hg["tolerations"] = json.loads(hg["tolerations"])

    converter = cattrs.Converter()
    converter.register_structure_hook(
        datetime,
        lambda ts, _: datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if isinstance(ts, str)
        else ts,
    )
    res = converter.structure(args, GenevaCluster)

    return res
