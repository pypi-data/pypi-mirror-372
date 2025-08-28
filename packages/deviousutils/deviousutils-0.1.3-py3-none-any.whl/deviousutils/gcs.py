import os, time, sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

def check_and_upload(weka_path, gcs_path):
    weka_path = weka_path.replace('weka://', '/')
    check_command = f"gsutil ls {gcs_path}"
    
    if os.system(check_command) != 0:
        command = f"""\
            gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" -m rsync -r {weka_path} {gcs_path} \
        """
        print(f'Executing command:\n{command}')
        os.system(command)
    else:
        print(f'Skipping {gcs_path} - already exists')


def check_and_download(gcs_path, local_path):
    check_command = f"test -d {local_path}"
    
    if os.system(check_command) != 0:
        command = f"""\
            gsutil -m cp -r {gcs_path} {local_path} \
        """
        print(f'Executing command:\n{command}')
        os.system(command)
    else:
        print(f'Skipping {local_path} - already exists')


if __name__ == "__main__":
    """
    python upload_gcs.py \
        --local_dir /oe-eval-default/ai2-llm/checkpoints/OLMo-medium/peteish13-highlr/step96000-unsharded \
        --remote_dir gs://ai2-llm/checkpoints/davidh/OLMo-medium/peteish13-highlr/step96000-unsharded
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local_dir", type=str, required=True, help="Local directory path to upload from")
    parser.add_argument("--remote_dir", type=str, required=True, help="GCS path to upload to")
    args = parser.parse_args()

    check_and_upload(args.local_dir, args.remote_dir)
