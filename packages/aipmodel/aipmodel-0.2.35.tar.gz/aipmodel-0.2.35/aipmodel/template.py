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
