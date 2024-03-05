import json
import tarfile
from io import BytesIO
from base64 import b64decode

from kfp import Client

KFP_TYPE_MAP = {
    "Integer": int,
    "Float": float,
    "Boolean": bool,
    "String": str,
    "JsonObject": json.loads
}

def transformer_disable_caching(op):
    op.execution_options.caching_strategy.max_cache_staleness = "P0D"

def get_artifact(
    client: Client,
    run_id: str,
    node_id: str,
    artifact_name: str,
) -> dict:
    """
    Source: https://github.com/kubeflow/pipelines/issues/4327#issuecomment-687255001
    """
    artifact = client.runs.read_artifact(
        run_id,
        node_id,
        artifact_name
    )
    data = b64decode(artifact.data)

    buffer = BytesIO()
    buffer.write(data)
    buffer.seek(0)
    with tarfile.open(fileobj=buffer) as tar:
        member_names = tar.getnames()
        data = {}
        for name in member_names:
            data[name] = tar.extractfile(name).read().decode('utf-8')

    return data