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
            data[name] = tar.extractfile(name).read().decode("utf-8")

    return data

def get_run_outputs(
    client: Client,
    run_id: str,
    normalize_output_names: bool = True,
) -> dict:
    run_data = client.get_run(run_id)
    run_manifest = json.loads(run_data.pipeline_runtime.workflow_manifest)

    all_output_data = {}
    for node in run_manifest["status"]["nodes"].values():
        # NOTE: Using type of node to find actual components (filtering out for-loops, subgraphs, etc)
        if node["type"] != "Pod":
            continue

        # Locate the associated template
        template = None
        for t in run_manifest["spec"]["templates"]:
            if t["name"] == node["templateName"]:
                template = t
        assert template is not None, "Template existence assumption broken"

        # Pull the type information from the spec
        component_spec = json.loads(
            template["metadata"]["annotations"]["pipelines.kubeflow.org/component_spec"]
        )
        # NOTE: We assume that orders match here (not 100% sure if that is valid)
        outputs = template["outputs"]["artifacts"]
        spec_outputs = component_spec["outputs"]

        type_info = {}
        for o, so in zip(outputs, spec_outputs):
            type_info[o["name"]] = so["type"]

        # Loop through artifacts and pull data then cast
        compontent_output_data = {}
        for artifact in node["outputs"]["artifacts"]:
            # Skip any artifact which is not an output (main-logs)
            if artifact["name"] not in type_info:
                continue

            output_data = get_artifact(
                client=client,
                run_id=run_id,
                node_id=node["id"],
                artifact_name=artifact["name"]
            )
            output_data = output_data["data"]

            # Cast types
            t = KFP_TYPE_MAP[type_info[artifact["name"]]]
            compontent_output_data[artifact["name"]] = t(output_data)

        if normalize_output_names:
            compontent_output_data = {
                k.replace(f"{node['templateName']}-", ""):v
                for k, v in compontent_output_data.items()
            }

        all_output_data[node["id"]] = compontent_output_data

    return all_output_data