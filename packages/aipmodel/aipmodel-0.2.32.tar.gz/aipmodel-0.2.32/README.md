# AIP Model SDK

This SDK provides a simple interface for registering, uploading, downloading, listing, and deleting machine learning models using ClearML and S3 (Ceph) as storage.

---

## Installation

Install from PyPI:

```bash
pip install aipmodel
```

---

## Authentication

You must provide your own **ClearML Access Key** and **Secret Key**, which you can obtain from:

[http://213.233.184.112:30080/](http://213.233.184.112:30080/) → Credentials section

---

## Example Usage

This example shows how to:

- Upload a local model
- Upload a Hugging Face model
- Upload a model from another S3
- Download a model
- List models
- Delete a model

```python
from dotenv import load_dotenv
from aipmodel.model_registry import MLOpsManager

load_dotenv()

manager = MLOpsManager(
    # The following values will be picked up from the environment variables (.env) by default.
    # You can uncomment and provide your own values below to override them.
    
    # clearml_api_server_url="your-endpoint_url",  
    # clearml_username="your-clearml-username",    
    # clearml_access_key="your-clearml-access-key",  
    # clearml_secret_key="your-clearml-secret-key" 
)

# STEP 2: Upload local model
print("\n--- STEP 2: Upload local model ---")
local_model_id = manager.add_model(
    source_type="local",
    model_name="your_local_model",
    source_path="path/to/your/local/model/folder",
    code_path="path/to/your/local/model/model.py",  # Optional
)
print(f"Local Model ID: {local_model_id}\n")

# STEP 3: Upload HuggingFace model
print("\n--- STEP 3: Upload HuggingFace model ---")
hf_model_id = manager.add_model(
    source_type="hf",
    model_name="your_hf_model",
    hf_source="facebook/wav2vec2-base-960h"
)
print(f"HuggingFace Model ID: {hf_model_id}\n")

# STEP 4: Upload model from your own S3 (e.g., AWS S3, MinIO, or Ceph)
print("\n--- STEP 4: Upload model from your own S3 ---")
s3_model_id = manager.add_model(
    source_type="s3",
    model_name="your_s3_model",
    external_ceph_endpoint_url="http://your-s3-endpoint.com",  # Example: "http://s3.example.com"
    external_ceph_bucket_name="your-s3-bucket",
    external_ceph_access_key="your-s3-access-key",
    external_ceph_secret_key="your-s3-secret-key",
    external_ceph_source_path="path/in/your/bucket/",  # Path to model in S3 bucket
    external_ceph_code_path="path/to/your/local/model/model.py"  # Optional, remove if not using a script
)
print(f"S3 Model ID: {s3_model_id}\n")

# STEP 5: Download a model locally
print("\n--- STEP 5: Download a model locally ---")
manager.get_model(
    model_name="your_hf_model",  # or any valid model name
    local_dest="./downloaded_model/",
)

# STEP 6: List all models in your AIP project
print("\n--- STEP 6: List all models ---")
manager.list_models()

# STEP 7: Get model information
print("\n--- STEP 7: Get model information ---")
manager.get_model_info("your_hf_model")

# STEP 8: Delete a model
print("\n--- STEP 8: Delete a model ---")
manager.delete_model(model_id=local_model_id)

```

---

## Functions Overview
## Functions Overview (Detailed)

| Function Name           | Input Type                                           | Example Input                                                                  | Output Type         | Example Output                                           | Terminal Output                                                                 |
|-------------------------|------------------------------------------------------|---------------------------------------------------------------------------------|---------------------|---------------------------------------------------------|---------------------------------------------------------------------------------|
| `create` (ProjectsAPI)   | `name: str, description: str`                        | `name="new_project", description="description of project"`                      | dict                | `{"id": "12345", "name": "new_project"}`                 | `[INFO] Created project 'new_project' with ID '12345'`                        |
| `get_all` (ProjectsAPI)  | None                                                 | None                                                                            | list                | `[{"id": "12345", "name": "new_project"}]`               | `[INFO] Retrieved all projects from ClearML`                                   |
| `create` (ModelsAPI)     | `name: str, project_id: str, metadata: dict, uri: str` | `name="new_model", project_id="12345", metadata={"key": "value"}, uri="uri"`   | dict                | `{"id": "67890", "name": "new_model"}`                   | `[INFO] Created model 'new_model' with ID '67890'`                             |
| `get_all` (ModelsAPI)    | `project_id: str`                                    | `project_id="12345"`                                                           | list                | `[{"id": "67890", "name": "new_model"}]`                 | `[INFO] Retrieved all models from ClearML project '12345'`                     |
| `update` (ModelsAPI)     | `model_id: str, uri: str, metadata: dict`             | `model_id="67890", uri="new_uri", metadata={"key": "new_value"}`               | dict                | `{"id": "67890", "uri": "new_uri", "metadata": {...}}`   | `[INFO] Updated model '67890' with new URI and metadata`                      |
| `get_by_id` (ModelsAPI)  | `model_id: str`                                      | `model_id="67890"`                                                             | dict                | `{"id": "67890", "name": "new_model", "uri": "uri"}`     | `[INFO] Retrieved model '67890' from ClearML`                                 |
| `delete` (ModelsAPI)     | `model_id: str`                                      | `model_id="67890"`                                                             | dict                | `{"status": "success", "message": "Model deleted"}`     | `[INFO] Deleted model '67890' from ClearML`                                   |
| `__init__` (MLOpsManager) | `CLEARML_API_SERVER_URL, CLEARML_USERNAME, ...`      | `CLEARML_API_SERVER_URL="url", CLEARML_USERNAME="user", ...`                    | None                | None                                                    | `[INFO] Initialized MLOpsManager`                                              |
| `add_model` (MLOpsManager) | `source_type: str, model_name: str, ...`             | `source_type="local", model_name="local_model", source_path="path/to/model"`   | str                 | `"model_id"`                                             | `[INFO] Model 'local_model' added successfully`                                |
| `get_model` (MLOpsManager) | `model_name: str, local_dest: str`                   | `model_name="local_model", local_dest="path/to/destination"`                   | dict                | `{"id": "12345", "name": "local_model"}`                 | `[INFO] Model 'local_model' downloaded successfully to 'path/to/destination'` |
| `list_models` (MLOpsManager) | None                                               | None                                                                            | list                | `[("model_name", "model_id")]`                           | `[INFO] Listing all models in project`                                          |
| `delete_model` (MLOpsManager) | `model_id: str, model_name: str`                    | `model_id="12345"`                                                             | None                | None                                                    | `[INFO] Model '12345' deleted successfully`                                    |
| `transfer_from_s3` (MLOpsManager) | `source_endpoint_url: str, ...`                   | `source_endpoint_url="http://s3.example.com", ...`                              | bool                | `True`                                                   | `[INFO] Transferred model from S3 successfully`                                |


| Function            | Description                                         |
| ------------------- | --------------------------------------------------- |
| `add_model(...)`    | Uploads a model from local, HF or external S3       |
| `get_model(...)`    | Downloads a model from S3 to local path             |
| `list_models()`     | Lists all registered models in your ClearML project |
| `delete_model(...)` | Deletes a model from ClearML and S3                 |

---

## Notes

- Ceph credentials (`s3.cloud-ai.ir`, access key, secret key) are hardcoded and used for final storage.
- Your own external S3 bucket is supported only during upload (optional).
- No config file is needed. You must pass ClearML keys manually in code.

---


## Admin Instructions: Auto-Publishing to PyPI

This SDK uses a GitHub Actions workflow (`.github/workflows/publish.yaml`) for automatic versioning and PyPI publishing.

### Trigger Conditions

- Must push to the `main` branch
- Must include `pipy commit -push` in the commit message
- Must have `PUBLISH_TO_PYPI=true` in GitHub project variables

### Commit Message Format

The following patterns control the version bump:

| Description Contains      | Resulting Bump                 |
| ------------------------- | ------------------------------ |
| `pipy commit -push major` | Increments **major**           |
| `pipy commit -push minor` | Increments **minor**           |
| `pipy commit -push patch` | Increments **patch**           |
| `pipy commit -push`       | Increments **patch** (default) |

### What Happens Automatically

- Version is read from PyPI
- New version is calculated using `bump_version.py`
- Version in `__init__.py` and `setup.py` is updated
- Changes are committed and pushed to `main`
- Package is built and published to PyPI via Twine

No manual work is needed from the admin.
