# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# manage ray cluster setup

"""
Why?
Setting up a cluster involves a lot of state and resource management
for different users the resources created during cluster setup can
include:
- Kuberay Cluster
- Portforwarding Server
- packaged zips
- ray context initialization

There are three issues:
1. We want to make sure the api for setting up a cluster is simple, which
means everything should be in a single place instead of requiring a bunch
of different context managers to be created. Consider
```python
with(
    KuberayCluster(),
    PortforwardingServer(),
    PackagedZips(),
    RayContextInit()
):
    # do something with the cluster
)
```
We do not want to require the user to do this. However if we keep everything
in a single context manager a second issue arises.

2. We want to make sure that the resources are cleaned up when the context
manager exits, that includes when resource setup fails. Doing this in a single
context manager is difficult. Consider
```python
def __enter__(self):
    try:
        do_kuberay_cluster_setup()
    except Exception as e:
        # cleanup resources
        raise e

    try:
        start_portforwarding_server()
    except Exception as e:
        # cleanup resources
        raise e

    ...

def __exit__(self, exc_type, exc_value, traceback):
    try:
        shutdown_ray_context()
    except Exception as e:
        # cleanup resources
        raise e

    try:
        shutdown_portforwarding_server()
    except Exception as e:
        # cleanup resources
        raise e

    ...
```

3. Users may want start at any one of the following points:
  - only has k8s + kuberay installed
  - has a ray cluster
  - has dependency already setup in the ray cluster
  We need a way to allow users to start at any one of these points

To solve the first two issues we create a setup_cluster func, to help with
entering and exiting the context manager
```python
with ray_cluster(
    cluster_settings={...},
    use_portforwarding=True,
    delete_packaged_zips=False,
    ...
) as m:
    # do something with the cluster
```
As long as the manager deligates the setup and teardown error handling
to contextlib.ExitStack, we can be sure that all resources are cleaned up
correctly.

The third issue is solved by allowing the user to pass in a ray address
to the setup_cluster function.
"""

import base64
import contextlib
import json
import logging
from collections.abc import Generator
from pathlib import Path

import pyarrow as pa
import ray

import geneva
from geneva.manifest.mgr import GenevaManifest
from geneva.packager.autodetect import upload_local_env
from geneva.packager.uploader import Uploader
from geneva.runners.ray._portforward import PortForward
from geneva.runners.ray.raycluster import RayCluster

_LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def init_ray(
    *,
    addr: str,
    zips: list[list[str]],
    pip: list[str] | None = None,
    local: bool = False,
    py_modules: list | None = None,
) -> Generator[None, None, None]:
    if ray.is_initialized():
        raise RuntimeError("Ray is already initialized, we cannot start a new cluster")

    geneva_zip_payload = base64.b64encode(
        json.dumps({"zips": zips}).encode("utf-8")
    ).decode("utf-8")

    # note: can we remove these to improve cold start times?
    default_modules = [geneva, pa]
    if not py_modules:
        py_modules = default_modules

    # modules result in "TypeError: cannot pickle 'module' object" in local ray
    modules = [] if local else py_modules

    runtime_env = {
        "env_vars": {
            "GENEVA_ZIPS": geneva_zip_payload,
        },
        **({"pip": pip} if pip else {}),
    }
    if modules:
        runtime_env.update(py_modules=modules)

    try:
        ray.init(
            addr,
            runtime_env=runtime_env,
        )
        yield
    except Exception:
        _LOG.exception(f"Failed to initialize ray: {addr}")
        raise
    finally:
        # shutdown ray when exiting the context manager
        ray.shutdown()


@contextlib.contextmanager
def ray_cluster(
    addr: str | None = None,
    *,
    use_portforwarding: bool = True,
    zip_output_dir: Path | str | None = None,
    uploader: Uploader | None = None,
    delete_local_packaged_zips: bool = False,
    skip_site_packages: bool = False,
    pip: list[str] | None = None,
    ray_cluster: RayCluster | None = None,
    manifest: GenevaManifest | None = None,
    local: bool = False,
    **ray_cluster_kwargs,
) -> Generator[None, None, None]:
    """
    Context manager for setting up a Ray cluster.

    Args:
        addr: The address of the Ray cluster. If None, a new cluster will be
            created.
        use_portforwarding: Whether to use port forwarding for the cluster.
            Defaults to True.
        zip_output_dir: The output directory for the zip files. If None, a
            temporary directory will be used.
        uploader: The uploader to use for uploading the zip files. If None,
            the default uploader will be used.
        delete_local_packaged_zips: Whether to delete the local zip files
            after uploading them. Defaults to False.
        skip_site_packages: Do not include files in site-packages in the manifest.
            Defaults to False.
        pip: A list of pip packages to install in the Ray cluster. If None,
            no pip packages will be installed.
        ray_cluster: An optional RayCluster. If provided, the ray_cluster_kwargs
            will be ignored.
        local: If set, will use a local Ray cluster using ray.init()
        **ray_cluster_kwargs: Additional arguments to pass to the RayCluster
            constructor.

    If addr is provided and use_portforwarding is True, a ValueError will be
    raised. This is because port forwarding is not supported for existing
    clusters.

    Similarly, if addr is None and ray_cluster_kwargs are provided, a
    ValueError will be raised.
    """
    if addr is not None and ray_cluster_kwargs:
        raise ValueError(
            "Cannot provide both addr and ray_cluster_kwargs. "
            "If addr is provided, use_portforwarding will be ignored."
        )

    # TODO: allow inspecting an existing RayCluster in k8s and allow
    # port forwarding to it
    # https://linear.app/lancedb/issue/GEN-23/define-geneva-ray-hookup-api-and-document
    if addr is not None and use_portforwarding:
        raise ValueError(
            "Cannot use port forwarding with an existing cluster. "
            "If addr is provided, use_portforwarding will be ignored."
        )

    with contextlib.ExitStack() as stack:
        if addr is None:
            if local:
                _LOG.info("starting local ray cluster")
            else:
                cluster = (
                    ray_cluster
                    if ray_cluster is not None
                    else RayCluster(**ray_cluster_kwargs)
                )
                ip = stack.enter_context(cluster)
                port = "10001"
                if use_portforwarding:
                    pf = stack.enter_context(PortForward.to_head_node(cluster))
                    ip = "localhost"
                    port = pf.local_port
                addr = f"ray://{ip}:{port}"
                _LOG.info(f"connecting to ray cluster at {addr}")

        py_modules = None
        if manifest is not None:
            # use a previously defined manifest
            zips = manifest.zips
            pip = manifest.pip
            py_modules = manifest.py_modules
        else:
            # build an ad-hoc manifest
            zips = (
                stack.enter_context(
                    upload_local_env(
                        zip_output_dir=zip_output_dir,
                        uploader=uploader,
                        delete_local_zips=delete_local_packaged_zips,
                        skip_site_packages=skip_site_packages,
                    )
                )
                if not local
                else []
            )

        stack.enter_context(
            init_ray(addr=addr, zips=zips, pip=pip, local=local, py_modules=py_modules)
        )

        yield
