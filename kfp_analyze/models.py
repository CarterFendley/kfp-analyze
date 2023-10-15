import json
from datetime import datetime
from dataclasses import dataclass
from typing import List

from graphviz import Digraph

def get_node_color(node_type: str):
    if node_type == 'Pod':
        return 'aqua'
    else:
        return 'azure3'

@dataclass
class KFPRun:
    manifest: dict

    def __post_init__(self):
        self._metadata = self.manifest['metadata']

    @property
    def run_id(self) -> str:
        return self._metadata['labels']['pipeline/runid']

    @property
    def run_name(self) -> str:
        return self._metadata['annotations']['pipelines.kubeflow.org/run_name']

    @property
    def phase(self) -> str:
        return self._metadata['labels']['workflows.argoproj.io/phase']

    @property
    def started_at(self) -> datetime:
        #return datetime.fromisoformat(self.manifest['status']['startedAt'])
        return self.manifest['status']['startedAt']
    @property
    def finished_at(self) -> datetime:
        #return datetime.fromisoformat(self.manifest['status']['finishedAt'])
        return self.manifest['status']['finishedAt']

    def get_pod_nodes(self) -> List['KFPPodNode']:
        pod_nodes = []
        for node in self.manifest['status']['nodes'].values():
            if node['type'] == 'Pod':
                pod_nodes.append(KFPPodNode(run=self, node=node))

        return pod_nodes

    def get_node(self, id: str) -> 'KFPPodNode':
        return KFPPodNode(
            run=self,
            node=self.manifest['status']['nodes'][id]
        )

    def graph_viz(self, raw=True) -> Digraph:
        dot = Digraph(self.manifest['metadata']['name'])

        edges = []
        for name, node in self.manifest['status']['nodes'].items():

            dot.node(
                name=name, 
                label=f"{node['displayName']} ({name})",
                tooltip=json.dumps(node, indent=4),
                style='filled',
                fillcolor=get_node_color(node['type'])
            )

            if 'children' in node:
                for child in node['children']:
                    edges.append((name, child))

        for edge in edges:
            dot.edge(*edge)

        return dot

    def to_record(self) -> dict:
        return {
            'run_id': self.run_id,
            'run_name': self.run_name,
            'run_status': self.phase,
            'run_start': self.started_at,
            'run_finish': self.finished_at
        }

@dataclass
class KFPPodNode:
    run: KFPRun
    node: dict

    def to_record(self) -> dict:
        record = {
            'stage_name': self.node['displayName']
        }
        record.update(self.run.to_record())

        return record

