import click
from kfp import Client
import pandas as pd

from kfp_analyze.ingestion import pull_run_data

@click.command()
@click.option('--host', help='The KFP host to connect to')
@click.option('--run-id')
def kfp_analyze(host: str, run_id: str):
    print('Pulling run data...')
    client = Client(host=host)
    run = pull_run_data(client=client, run_id=run_id)

    print('Parsing run data...')
    pods = run.get_pod_nodes()
    df = pd.DataFrame([pod.to_record() for pod in pods])

    output_path = f'{run_id}.xlsx'
    print(f'Writing data to: {output_path}')
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='data', index=False)

        worksheet = writer.sheets['data']
        worksheet.set_column('B:B', None, None, {'hidden': 1})
