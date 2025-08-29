# test_mlops_manager.py
# Import required modules
import os
import logging
from dotenv import load_dotenv
import model_registry

# Setup logging to capture detailed execution traces
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s",
    handlers=[
        logging.FileHandler("test_mlops_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Paths and configurations for testing
MODEL_FOLDER = r"D:\university\Master-Terms\DML\Projects\MLOPS\Test\Qwen2.5-14B-Instruct"  
HUGGINGFACE_MODEL = "distilbert-base-uncased"  # Lightweight Hugging Face model for testing
EXTERNAL_S3_CONFIG = {
    "source_access_key": "X3YCDZPMPE5A677TR6NZ",
    "source_endpoint_url": "https://s3.cloud-ai.ir", 
    "source_secret_key": "8M3s4saHPk9tgT1T7eA46JoHzdlZ6CJeMaBw51Gl", 
    "source_bucket_name": "almmlops",  
    "model_name": "Rayen/YOLO", 
    "model_path": "models/yolo/yolo12n.pt", 
    # "model_id": "875ee9be5b654f9a80d3cf85fa40c1a0" 
}
TEST_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "mlops")  # Fallback to 'mlops' if env var not set

# Global mlops instance (initialized once)
mlops = None

def initialize_mlops():
    """Initialize MLOpsManager once for all tests."""
    global mlops
    try:
        mlops = model_registry.MLOpsManager(
            CLEARML_API_SERVER_URL=os.environ.get("CLEARML_API_HOST"),
            CLEARML_USERNAME=os.environ.get("CLEARML_USERNAME"),
            CLEARML_ACCESS_KEY=os.environ.get("CLEARML_API_ACCESS_KEY"),
            CLEARML_SECRET_KEY=os.environ.get("CLEARML_API_SECRET_KEY")
        )
        logger.info("MLOpsManager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MLOpsManager: {e}")
        raise

# Individual test functions
def test_projects_create():
    try:
        result = mlops.projects.create(name="test_project", description="Test project")
        logger.info(f"ProjectsAPI.create(name='test_project', description='Test project') -> {result}")
        # TODO: Replace 'test_project' with actual ClearML project name if needed
    except Exception as e:
        logger.error(f"ProjectsAPI.create failed: {e}")

def test_projects_get_all():
    try:
        result = mlops.projects.get_all()
        logger.info(f"ProjectsAPI.get_all() -> {result}")
    except Exception as e:
        logger.error(f"ProjectsAPI.get_all failed: {e}")

def test_models_get_all():
    try:
        result = mlops.models.get_all(project_id=mlops.project_id)
        logger.info(f"ModelsAPI.get_all(project_id={mlops.project_id}) -> {result}")
    except Exception as e:
        logger.error(f"ModelsAPI.get_all failed: {e}")

def test_models_create():
    try:
        result = mlops.models.create(name="qwen2.5-14b-instruct", project_id=mlops.project_id, uri=f"s3://{TEST_BUCKET_NAME}/qwen2.5-14b-instruct/")
        logger.info(f"ModelsAPI.create(name='qwen2.5-14b-instruct', project_id={mlops.project_id}, uri='s3://{TEST_BUCKET_NAME}/qwen2.5-14b-instruct/') -> {result}")
        # TODO: Replace 'qwen2.5-14b-instruct' and uri with actual model name and S3 path if needed
    except Exception as e:
        logger.error(f"ModelsAPI.create failed: {e}")

def test_models_get_by_id():
    try:
        models = mlops.models.get_all(project_id=mlops.project_id)
        model_id = models[0]["id"] if models else "dummy_id"  # TODO: Replace 'dummy_id' with actual model_id from your ClearML project
        result = mlops.models.get_by_id(model_id)
        logger.info(f"ModelsAPI.get_by_id(model_id={model_id}) -> {result}")
    except Exception as e:
        logger.error(f"ModelsAPI.get_by_id failed: {e}")

def test_models_update():
    try:
        models = mlops.models.get_all(project_id=mlops.project_id)
        model_id = models[0]["id"] if models else "dummy_id"  # TODO: Replace 'dummy_id' with actual model_id from your ClearML project
        result = mlops.models.update(model_id, metadata={"test_key": "test_value"})
        logger.info(f"ModelsAPI.update(model_id={model_id}, metadata={{'test_key': 'test_value'}}) -> {result}")
    except Exception as e:
        logger.error(f"ModelsAPI.update failed: {e}")

def test_models_edit_uri():
    try:
        models = mlops.models.get_all(project_id=mlops.project_id)
        model_id = models[0]["id"] if models else "dummy_id"  # TODO: Replace 'dummy_id' with actual model_id from your ClearML project
        result = mlops.models.edit_uri(model_id, uri=f"s3://{TEST_BUCKET_NAME}/qwen2.5-14b-instruct_updated/")
        logger.info(f"ModelsAPI.edit_uri(model_id={model_id}, uri='s3://{TEST_BUCKET_NAME}/qwen2.5-14b-instruct_updated/') -> {result}")
        # TODO: Replace uri with actual S3 path if needed
    except Exception as e:
        logger.error(f"ModelsAPI.edit_uri failed: {e}")

def test_models_delete():
    try:
        models = mlops.models.get_all(project_id=mlops.project_id)
        model_id = models[0]["id"] if models else "dummy_id"  # TODO: Replace 'dummy_id' with actual model_id from your ClearML project
        result = mlops.models.delete(model_id)
        logger.info(f"ModelsAPI.delete(model_id={model_id}) -> {result}")
        # TODO: Ensure you want to delete this model_id before running
    except Exception as e:
        logger.error(f"ModelsAPI.delete failed: {e}")

def test_get_model_id_by_name():
    try:
        result = mlops.get_model_id_by_name("qwen2.5-14b-instruct")
        logger.info(f"get_model_id_by_name(name='qwen2.5-14b-instruct') -> {result}")
        # TODO: Replace 'qwen2.5-14b-instruct' with actual model name from your ClearML project if needed
    except Exception as e:
        logger.error(f"get_model_id_by_name failed: {e}")

def test_get_model_name_by_id():
    try:
        models = mlops.models.get_all(project_id=mlops.project_id)
        model_id = models[0]["id"] if models else "dummy_id"  # TODO: Replace 'dummy_id' with actual model_id from your ClearML project
        result = mlops.get_model_name_by_id(model_id)
        logger.info(f"get_model_name_by_id(model_id={model_id}) -> {result}")
    except Exception as e:
        logger.error(f"get_model_name_by_id failed: {e}")

def test_generate_random_string():
    try:
        result = mlops.generate_random_string()
        logger.info(f"generate_random_string() -> {result}")
    except Exception as e:
        logger.error(f"generate_random_string failed: {e}")

def test_transfer_from_s3():
    try:
        result = mlops.transfer_from_s3(
            source_endpoint_url=EXTERNAL_S3_CONFIG["source_endpoint_url"],
            source_access_key=EXTERNAL_S3_CONFIG["source_access_key"],
            source_secret_key=EXTERNAL_S3_CONFIG["source_secret_key"],
            source_bucket=EXTERNAL_S3_CONFIG["source_bucket_name"],
            source_path=EXTERNAL_S3_CONFIG["model_path"],
            dest_prefix=f"models/whisper-large-v2-fa/"  # TODO: Replace with actual destination prefix if needed
        )
        logger.info(f"transfer_from_s3(source_path='{EXTERNAL_S3_CONFIG['model_path']}', dest_prefix='models/whisper-large-v2-fa/') -> {result}")
    except Exception as e:
        logger.error(f"transfer_from_s3 failed: {e}")

def test_add_model_local():
    try:
        result = mlops.add_model(
            source_type="local",
            model_name="qwen2.5-14b-instruct",
            source_path=MODEL_FOLDER
        )
        logger.info(f"add_model(source_type='local', model_name='qwen2.5-14b-instruct', source_path='{MODEL_FOLDER}') -> {result}")
        
    except Exception as e:
        logger.error(f"add_model (local) failed: {e}")

def test_add_model_huggingface():
    try:
        result = mlops.add_model(
            source_type="hf",
            model_name="distilbert-base-uncased",
            source_path=HUGGINGFACE_MODEL
        )
        logger.info(f"add_model(source_type='hf', model_name='distilbert-base-uncased', source_path='{HUGGINGFACE_MODEL}') -> {result}")
        # TODO: Replace 'distilbert-base-uncased' with actual Hugging Face model ID if needed
    except Exception as e:
        logger.error(f"add_model (huggingface) failed: {e}")

def test_add_model_s3():
    try:
        result = mlops.add_model(
            source_type="s3",
            model_name=EXTERNAL_S3_CONFIG["model_name"],
            source_path=EXTERNAL_S3_CONFIG["model_path"],
            access_key=EXTERNAL_S3_CONFIG["source_access_key"],
            secret_key=EXTERNAL_S3_CONFIG["source_secret_key"],
            endpoint_url=EXTERNAL_S3_CONFIG["source_endpoint_url"],
            bucket_name=EXTERNAL_S3_CONFIG["source_bucket_name"]
        )
        logger.info(f"add_model(source_type='s3', model_name='{EXTERNAL_S3_CONFIG['model_name']}', source_path='{EXTERNAL_S3_CONFIG['model_path']}') -> {result}")
        # TODO: Replace EXTERNAL_S3_CONFIG values with actual S3 credentials and model path if needed
    except Exception as e:
        logger.error(f"add_model (s3) failed: {e}")

def test_get_model():
    try:
        result = mlops.get_model("qwen2.5-14b-instruct", local_dest=r"C:\Users\ASUS\Desktop")
        logger.info(f"get_model(model_name='qwen2.5-14b-instruct', local_dest='C:\\Users\\ASUS\\Desktop') -> {result}")
        # TODO: Replace 'qwen2.5-14b-instruct' with actual model name and local_dest with valid path if needed
    except Exception as e:
        logger.error(f"get_model failed: {e}")

def test_get_model_info():
    try:
        result = mlops.get_model_info("distilbert-base-uncased")
        logger.info(f"get_model_info(identifier='distilbert-base-uncased') -> {result}")
        # TODO: Replace 'qwen2.5-14b-instruct' with actual model name or ID from your ClearML project if needed
    except Exception as e:
        logger.error(f"get_model_info failed: {e}")

def test_list_models():
    try:
        result = mlops.list_models(verbose=True)
        logger.info(f"list_models(verbose=True) -> {result}")
    except Exception as e:
        logger.error(f"list_models failed: {e}")

def test_delete_model():
    try:
        result = mlops.delete_model(model_name="qwen2.5-14b-instruct")
        logger.info(f"delete_model(model_name='qwen2.5-14b-instruct') -> {result}")
        # TODO: Replace 'qwen2.5-14b-instruct' with actual model name or ID from your ClearML project; ensure you want to delete
    except Exception as e:
        logger.error(f"delete_model failed: {e}")

def main():
    """Run individual tests by uncommenting them one by one."""
    logger.info("Starting MLOpsManager test suite")
    initialize_mlops()  # Initialize once

    # Uncomment one test at a time to run it
    # test_projects_create()
    # test_projects_get_all()
    # test_models_get_all()
    # test_models_create()
    # test_models_get_by_id()
    # test_models_update()
    # test_models_edit_uri()
    # test_models_delete()
    # test_get_model_id_by_name()
    # test_get_model_name_by_id()
    # test_generate_random_string()
    # test_transfer_from_s3()
    
    # test_delete_model()
    # test_add_model_local()
    # test_add_model_huggingface()
    # test_add_model_s3()
    # test_get_model()
    # test_get_model_info()
    # test_list_models()
    # test_delete_model()

    logger.info("MLOpsManager test suite completed (uncomment tests to run them)")

if __name__ == "__main__":
    main()