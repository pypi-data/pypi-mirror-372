import os
import pandas as pd
from huggingface_hub import HfApi, login, hf_hub_download
from pathlib import Path

DATA_DIR = Path.home() / ".cache" / "deviousutils"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def push_parquet_to_hf(file_path, hf_dataset_name, split_name='main', subset_name="data", private=True, overwrite=False):
    file_suffix = Path(file_path).suffix
    if file_suffix == '.parquet':
        import pyarrow.parquet as pq
        print('Loading sanity check...')
        df = pq.read_table(file_path).slice(0, 100).to_pandas()
        pd.set_option('display.max_columns', None)
        print(df)
    elif file_suffix == '.jsonl':
        import json
        print('Loading sanity check...')
        with open(file_path, 'r') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 100:
                    break
                lines.append(json.loads(line.strip()))
        df = pd.DataFrame(lines)
        pd.set_option('display.max_columns', None)
        print(df)

    login(new_session=False)
    api = HfApi()
    
    # Check if the repo exists; create it if not
    try:
        api.repo_info(repo_id=hf_dataset_name, repo_type="dataset")
    except Exception as e:
        api.create_repo(repo_id=hf_dataset_name, private=private, repo_type="dataset", exist_ok=True)

    # Determine the target file path in the repository
    # https://huggingface.co/docs/hub/en/datasets-file-names-and-splits
    path_in_repo = os.path.join(subset_name, f'{split_name}-00000-of-00001' + file_suffix) 

    # Check if the file exists in the repository
    repo_files = api.list_repo_files(repo_id=hf_dataset_name, repo_type="dataset")
    if path_in_repo in repo_files:
        if not overwrite:
            print(f"File '{path_in_repo}' already exists in '{hf_dataset_name}'. Skipping upload.")
            return
        print(f"File '{path_in_repo}' exists and will be overwritten.")

    print(f"Uploading '{file_path}' -> '{path_in_repo}' to hf dataset '{hf_dataset_name}'")

    # Upload the file to the repository
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=path_in_repo,
        repo_id=hf_dataset_name,
        repo_type="dataset"
    )
    print(f"File '{path_in_repo}' uploaded to '{hf_dataset_name}'.")


def pull_parquet_from_hf(repo_id, split_name, subset_name='data', local_path=DATA_DIR, filetype='parquet'):
    file_name = f'{subset_name}/{split_name}-00000-of-00001.{filetype}'
    if 'all' in file_name: file_name = file_name.replace('-00000-of-00001', '')
    print(f'Downloading {file_name} -> {local_path}')
    local_file_name = hf_hub_download(
        repo_id=repo_id,
        filename=file_name,
        repo_type="dataset",
        local_dir=local_path
    )
    local_file_name = os.path.join(local_path, file_name)
    return local_file_name
