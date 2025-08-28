Deviously useful utilities

```sh
pip install deviousutils
```

### HF Utils

```python
from deviousutils.hf import push_parquet_to_hf, pull_parquet_from_hf

push_parquet_to_hf(file_path, hf_dataset_name)
local_path = pull_parquet_from_hf(repo_id, split_name)
```

### OpenAI Utils

```python
from deviousutils.openai import openai_init, generate_gpt, print_estimate_cost

openai_init()
print(print_estimate_cost(prompts))
responses = generate_gpt(prompts)
```

### GCS Utils

```python
from deviousutils.gcs import check_and_upload, check_and_download

check_and_upload(weka_path, gcs_path)
check_and_download(gcs_path, local_path)
```
