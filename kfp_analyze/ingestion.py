import json
import logging

from kfp import Client

from .models import KFPRun

def pull_run_data(client: Client, run_id: str) -> KFPRun:
    manifest = json.loads(
        client.get_run(run_id).pipeline_runtime.workflow_manifest
    )

    if manifest['status']['phase'] not in ('Succeeded', 'Failed'):
        logging.warning("KFP Run '%s' has not finished, this will result in undefined behavior" % run_id)

    return KFPRun(manifest)