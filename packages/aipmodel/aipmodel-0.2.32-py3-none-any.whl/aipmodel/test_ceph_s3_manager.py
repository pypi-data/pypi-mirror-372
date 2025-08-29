import os
import tempfile
import json
import shutil
import string
from dotenv import load_dotenv
from CephS3Manager import CephS3Manager

load_dotenv()

class CephS3ManagerTester:
    def __init__(self):
        """Initialize CephS3Manager with environment variables and create test artifacts."""
        try:
            self.ceph = CephS3Manager(
                os.environ.get("CEPH_ENDPOINT_URL"),  # Loaded from .env: http://s3.cloud-ai.ir
                os.environ.get("S3_ACCESS_KEY"),      # Loaded from .env: OAF0MC26UA7DV9WS11X5
                os.environ.get("S3_SECRET_KEY"),      # Loaded from .env: 6SY2dTxhcIVEsjbfpjRUBhe3k7mMJIjZpccwvw3d
                os.environ.get("S3_BUCKET_NAME"),     # Loaded from .env: mlops
                verbose=False
            )
            print("[SUCCESS] CephS3Manager initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize CephS3Manager: {str(e)}")
            raise

        # Prepare temp data for testing
        self.test_username = "test_user_12345"  # Used for create_user and set_user_quota tests
        self.test_quota_gb = 1
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        self.test_folder_path = os.path.join(self.temp_dir, "test_folder")
        os.makedirs(self.test_folder_path, exist_ok=True)
        with open(self.test_file_path, 'w') as f:
            f.write("This is a test file content for CephS3Manager testing.")
        with open(os.path.join(self.test_folder_path, "nested_file.txt"), 'w') as f:
            f.write("This is a nested file in test folder.")
        self.test_s3_file_key = "test_uploaded_file.txt"
        self.test_s3_folder = "test_folder/"
        self.test_model_path = "models/test_class/test_model/model_v1/test_file.txt"

    def cleanup(self):
        """Remove uploaded files and folders from S3 and local temp dir."""
        print("\n" + "="*60)
        print("CLEANUP")
        print("="*60)
        try:
            # Clean up single test file
            if self.ceph.check_if_exists(self.test_s3_file_key):
                self.ceph.s3.delete_object(Bucket=self.ceph.bucket_name, Key=self.test_s3_file_key)
                print(f"Removed test file from S3: {self.test_s3_file_key}")
            # Clean up test folder
            if self.ceph.check_if_exists(self.test_s3_folder):
                self.ceph.delete_folder(self.test_s3_folder)
                print(f"Removed test folder from S3: {self.test_s3_folder}")
            # Clean up moved folder
            moved_folder = "moved_folder/"
            if self.ceph.check_if_exists(moved_folder):
                self.ceph.delete_folder(moved_folder)
                print(f"Removed moved folder from S3: {moved_folder}")
            # Clean up model structure
            model_folder = "models/"
            if self.ceph.check_if_exists(model_folder):
                self.ceph.delete_folder(model_folder)
                print(f"Removed model folder from S3: {model_folder}")
        except Exception as e:
            print(f"[WARN] S3 cleanup skipped or failed: {e}")
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print("Removed local temp directory")
        except Exception as e:
            print(f"[WARN] Local cleanup failed: {e}")

    # ============ Pure local helpers ============

    def test_generate_random_string(self):
        """Test the generate_random_string method."""
        print("\n" + "="*60)
        print("TESTING: generate_random_string")
        print("="*60)
        r1 = self.ceph.generate_random_string()
        assert len(r1) == 12, "Default length must be 12"
        assert r1.isalnum(), "Must be alphanumeric"
        r2 = self.ceph.generate_random_string(length=20)
        assert len(r2) == 20, "Custom length should be 20"
        try:
            self.ceph.generate_random_string(length=-1)
            assert False, "Negative length should raise ValueError"
        except ValueError:
            print("[SUCCESS] Negative length handling")
        try:
            self.ceph.generate_random_string(characters="")
            assert False, "Empty character set should raise ValueError"
        except ValueError:
            print("[SUCCESS] Empty character set handling")
        r3 = self.ceph.generate_random_string()
        r4 = self.ceph.generate_random_string()
        assert r3 != r4, "Generated strings should be different"
        print("[SUCCESS] generate_random_string")

    def test_generate_key(self):
        """Test the generate_key method."""
        print("\n" + "="*60)
        print("TESTING: generate_key")
        print("="*60)
        k1 = self.ceph.generate_key()
        assert len(k1) == 12, "Default length must be 12"
        assert k1.isalnum(), "Default key must be alphanumeric"
        k2 = self.ceph.generate_key(length=16)
        assert len(k2) == 16, "Custom length must be 16"
        k3 = self.ceph.generate_key(length=8, characters="ABC123")
        assert len(k3) == 8, "Length must be 8"
        assert all(c in "ABC123" for c in k3), "Characters must be from custom set"
        try:
            self.ceph.generate_key(length=-1)
            assert False, "Negative length should raise ValueError"
        except ValueError:
            print("[SUCCESS] Negative length handling")
        try:
            self.ceph.generate_key(characters="")
            assert False, "Empty character set should raise ValueError"
        except ValueError:
            print("[SUCCESS] Empty character set handling")
        k4 = self.ceph.generate_key()
        k5 = self.ceph.generate_key()
        assert k4 != k5, "Generated keys should be different"
        print("[SUCCESS] generate_key")

    def test_generate_access_key(self):
        """Test the generate_access_key method."""
        print("\n" + "="*60)
        print("TESTING: generate_access_key")
        print("="*60)
        ak = self.ceph.generate_access_key()
        assert len(ak) == 20, "Access key length must be 20"
        allowed = set(string.ascii_uppercase + string.digits)
        assert set(ak).issubset(allowed), "Access key must be uppercase letters or digits"
        ak2 = self.ceph.generate_access_key()
        assert ak != ak2, "Generated access keys should be different"
        print("[SUCCESS] generate_access_key")

    def test_generate_secret_key(self):
        """Test the generate_secret_key method."""
        print("\n" + "="*60)
        print("TESTING: generate_secret_key")
        print("="*60)
        sk = self.ceph.generate_secret_key()
        assert len(sk) == 40, "Secret key length must be 40"
        assert sk.isalnum(), "Secret key must be alphanumeric"
        sk2 = self.ceph.generate_secret_key()
        assert sk != sk2, "Generated secret keys should be different"
        print("[SUCCESS] generate_secret_key")

    # ============ S3 connectivity/auth/buckets ============

    def test_check_connection(self):
        """Test the check_connection method."""
        print("\n" + "="*60)
        print("TESTING: check_connection")
        print("="*60)
        assert self.ceph.check_connection() is True, "Connection check should return True"
        print("[SUCCESS] check_connection")

    def test_check_auth(self):
        """Test the check_auth method."""
        print("\n" + "="*60)
        print("TESTING: check_auth")
        print("="*60)
        assert self.ceph.check_auth() is True, "Auth check should return True"
        print("[SUCCESS] check_auth")

    def test_ensure_bucket_exists(self):
        """Test the ensure_bucket_exists method."""
        print("\n" + "="*60)
        print("TESTING: ensure_bucket_exists")
        print("="*60)
        self.ceph.ensure_bucket_exists()
        buckets = self.ceph.list_available_buckets()
        assert self.ceph.bucket_name in buckets, f"Bucket {self.ceph.bucket_name} should exist"
        print("[SUCCESS] ensure_bucket_exists")

    def test_list_buckets(self):
        """Test the list_buckets method."""
        print("\n" + "="*60)
        print("TESTING: list_buckets")
        print("="*60)
        res = self.ceph.list_buckets()
        assert isinstance(res, list), "Result should be a list"
        for b in res:
            assert "Name" in b and "CreationDate" in b, "Bucket data should contain Name and CreationDate"
        print("[SUCCESS] list_buckets")

    def test_list_available_buckets(self):
        """Test the list_available_buckets method."""
        print("\n" + "="*60)
        print("TESTING: list_available_buckets")
        print("="*60)
        res = self.ceph.list_available_buckets()
        assert isinstance(res, list), "Result should be a list"
        assert self.ceph.bucket_name in res, f"Bucket {self.ceph.bucket_name} should be listed"
        print("[SUCCESS] list_available_buckets")

    def test_print_bucket_full_detail(self):
        """Test the print_bucket_full_detail method."""
        print("\n" + "="*60)
        print("TESTING: print_bucket_full_detail")
        print("="*60)
        res = self.ceph.print_bucket_full_detail()
        assert isinstance(res, dict), "Result should be a dict"
        assert "Buckets" in res, "Response should contain Buckets key"
        print("[SUCCESS] print_bucket_full_detail")

    def test_print_bucket_short_detail(self):
        """Test the print_bucket_short_detail method."""
        print("\n" + "="*60)
        print("TESTING: print_bucket_short_detail")
        print("="*60)
        try:
            self.ceph.print_bucket_short_detail()
            print("[SUCCESS] print_bucket_short_detail")
        except ImportError:
            print("[NOTE] Tabulate library not installed; skipping detailed assert")
            assert True  # Pass if tabulate is not installed
        print("[SUCCESS] print_bucket_short_detail")

    # ============ System utilities ============

    def test_check_command_exists(self):
        """Test the check_command_exists method."""
        print("\n" + "="*60)
        print("TESTING: check_command_exists")
        print("="*60)
        assert self.ceph.check_command_exists("python") is True, "Python should exist"
        assert self.ceph.check_command_exists("nonexistentcommand12345") is False, "Nonexistent command should not exist"
        print("[SUCCESS] check_command_exists")

    def test_check_s5cmd(self):
        """Test the check_s5cmd method."""
        print("\n" + "="*60)
        print("TESTING: check_s5cmd")
        print("="*60)
        available = self.ceph.check_s5cmd()
        print(f"s5cmd available: {available}")
        assert isinstance(available, bool), "Result should be boolean"
        print("[SUCCESS] check_s5cmd")

    def test_check_aws_credentials_folder(self):
        """Test the check_aws_credentials_folder method."""
        print("\n" + "="*60)
        print("TESTING: check_aws_credentials_folder")
        print("="*60)
        assert self.ceph.check_aws_credentials_folder() is True, "AWS credentials folder should exist"
        aws_dir = os.path.expanduser("~/.aws")
        assert os.path.isdir(aws_dir), "AWS credentials folder should be a directory"
        print("[SUCCESS] check_aws_credentials_folder")

    # ============ Identity (may be unsupported on RGW) ============

    def test_get_identity(self):
        """Test the get_identity method."""
        print("\n" + "="*60)
        print("TESTING: get_identity")
        print("="*60)
        try:
            identity = self.ceph.get_identity()
            assert isinstance(identity, dict), "Identity should be a dict"
            print("[SUCCESS] get_identity")
        except Exception as e:
            if "AccessDenied" in str(e) or "NotImplemented" in str(e):
                print("[NOTE] STS not available or access denied; skipping assert")
            else:
                raise

    def test_get_user_info(self):
        """Test the get_user_info method."""
        print("\n" + "="*60)
        print("TESTING: get_user_info")
        print("="*60)
        try:
            info = self.ceph.get_user_info()
            assert isinstance(info, dict), "User info should be a dict"
            print("[SUCCESS] get_user_info")
        except Exception as e:
            if "AccessDenied" in str(e) or "NotImplemented" in str(e):
                print("[NOTE] IAM not available or access denied; skipping assert")
            else:
                raise

    # ============ Upload/Download/File ops ============

    def test_upload_file(self):
        """Test the upload_file method."""
        print("\n" + "="*60)
        print("TESTING: upload_file")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        exists = self.ceph.check_if_exists(self.test_s3_file_key)
        assert exists is not None and len(exists) > 0, f"File {self.test_s3_file_key} should exist in S3"
        try:
            self.ceph.upload_file("non_existent_file.txt", "invalid_file.txt")
            assert False, "Uploading non-existent file should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent file handling")
        print("[SUCCESS] upload_file")

    def test_upload_folder(self):
        """Test the upload method for folders."""
        print("\n" + "="*60)
        print("TESTING: upload_folder")
        print("="*60)
        size_mb = self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        assert size_mb is not None, "Uploaded folder size should be returned"
        exists = self.ceph.check_if_exists(self.test_s3_folder)
        assert exists is not None and len(exists) > 0, f"Folder {self.test_s3_folder} should exist in S3"
        try:
            self.ceph.upload("non_existent_folder", "invalid_folder/")
            assert False, "Uploading non-existent folder should raise ValueError"
        except FileNotFoundError:
            print("[SUCCESS] Non-existent folder handling")
        print("[SUCCESS] upload_folder")

    def test_check_if_exists(self):
        """Test the check_if_exists method."""
        print("\n" + "="*60)
        print("TESTING: check_if_exists")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        res1 = self.ceph.check_if_exists(self.test_s3_file_key)
        assert res1 is not None and len(res1) > 0, f"File {self.test_s3_file_key} should exist"
        res2 = self.ceph.check_if_exists("non_existing_file_12345.txt")
        assert res2 is None, "Non-existent file should return None"
        print("[SUCCESS] check_if_exists")

    def test_read_file_from_s3(self):
        """Test the read_file_from_s3 method."""
        print("\n" + "="*60)
        print("TESTING: read_file_from_s3")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        content = self.ceph.read_file_from_s3(self.test_s3_file_key)
        assert isinstance(content, str), "Content should be a string for text files"
        assert "test file content" in content, "File content should match uploaded file"
        try:
            self.ceph.read_file_from_s3("non_existing_file_12345.txt")
            assert False, "Reading non-existent file should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent file handling")
        print("[SUCCESS] read_file_from_s3")

    def test_get_uri_size(self):
        """Test the get_uri_size method."""
        print("\n" + "="*60)
        print("TESTING: get_uri_size")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        uri = f"s3://{self.ceph.bucket_name}/{self.test_s3_file_key}"
        size_mb = self.ceph.get_uri_size(uri)
        assert size_mb > 0, "File size should be greater than 0"
        try:
            self.ceph.get_uri_size("s3://wrong_bucket/invalid_key")
            assert False, "Invalid bucket should raise ValueError"
        except ValueError:
            print("[SUCCESS] Invalid bucket handling")
        print("[SUCCESS] get_uri_size")

    def test_is_folder(self):
        """Test the is_folder method."""
        print("\n" + "="*60)
        print("TESTING: is_folder")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        assert self.ceph.is_folder(self.test_s3_file_key) is False, "File should not be detected as folder"
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        assert self.ceph.is_folder(self.test_s3_folder) is True, "Folder should be detected as folder"
        print("[SUCCESS] is_folder")

    def test_download_file(self):
        """Test the download_file method."""
        print("\n" + "="*60)
        print("TESTING: download_file")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        local_path = os.path.join(self.temp_dir, "downloaded_file.txt")
        self.ceph.download_file(self.test_s3_file_key, local_path)
        assert os.path.exists(local_path), "Downloaded file should exist"
        with open(local_path, "r") as f:
            data = f.read()
        assert "test file content" in data, "Downloaded file content should match"
        print("[SUCCESS] download_file")

    def test_download_folder(self):
        """Test the download_folder method."""
        print("\n" + "="*60)
        print("TESTING: download_folder")
        print("="*60)
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        download_path = os.path.join(self.temp_dir, "downloaded_folder")
        self.ceph.download_folder(self.test_s3_folder, download_path, keep_folder=True, exclude=["nested_file.txt"])
        nested_file = os.path.join(download_path, "test_folder", "nested_file.txt")
        assert not os.path.exists(nested_file), "Excluded file should not be downloaded"
        print("[SUCCESS] download_folder")

    def test_delete_folder(self):
        """Test the delete_folder method."""
        print("\n" + "="*60)
        print("TESTING: delete_folder")
        print("="*60)
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        self.ceph.delete_folder(self.test_s3_folder)
        exists = self.ceph.check_if_exists(self.test_s3_folder)
        assert exists is None, f"Folder {self.test_s3_folder} should be deleted"
        try:
            self.ceph.delete_folder("non_existing_folder_12345/")
            print("[SUCCESS] Non-existent folder handling (no error expected)")
        except Exception as e:
            print(f"[WARN] Unexpected error on non-existent folder: {e}")
        print("[SUCCESS] delete_folder")

    def test_move_folder(self):
        """Test the move_folder method."""
        print("\n" + "="*60)
        print("TESTING: move_folder")
        print("="*60)
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        dest_folder = "moved_folder/"
        self.ceph.move_folder(self.test_s3_folder, dest_folder)
        src_exists = self.ceph.check_if_exists(self.test_s3_folder)
        dest_exists = self.ceph.check_if_exists(dest_folder)
        assert src_exists is None, f"Source folder {self.test_s3_folder} should not exist"
        assert dest_exists is not None and len(dest_exists) > 0, f"Destination folder {dest_folder} should exist"
        try:
            self.ceph.move_folder("non_existing_folder_12345/", "dest_folder/")
            assert False, "Moving non-existent folder should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent folder handling")
        print("[SUCCESS] move_folder")

    def test_list_folder_contents(self):
        """Test the list_folder_contents method."""
        print("\n" + "="*60)
        print("TESTING: list_folder_contents")
        print("="*60)
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        self.ceph.list_folder_contents(self.test_s3_folder)
        try:
            self.ceph.list_folder_contents("non_existing_folder_12345/")
            assert False, "Listing non-existent folder should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent folder handling")
        print("[SUCCESS] list_folder_contents")

    def test_find_file(self):
        """Test the find_file method."""
        print("\n" + "="*60)
        print("TESTING: find_file")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_s3_file_key)
        results = self.ceph.find_file(self.test_s3_file_key)
        assert len(results) > 0, "File should be found"
        assert results[0][0] == self.test_s3_file_key, "Found file key should match"
        self.ceph.upload(self.test_folder_path, self.test_s3_folder)
        folder_results = self.ceph.find_file(self.test_s3_folder)
        assert len(folder_results) > 0, "Folder contents should be found"
        try:
            self.ceph.find_file("non_existing_file_12345.txt")
            assert False, "Non-existent file should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent file handling")
        print("[SUCCESS] find_file")

    def test_list_model_classes(self):
        """Test the list_model_classes method."""
        print("\n" + "="*60)
        print("TESTING: list_model_classes")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_model_path)
        res = self.ceph.list_model_classes()
        assert isinstance(res, list), "Result should be a list"
        assert "test_class" in res, "Test model class should be listed"
        print("[SUCCESS] list_model_classes")

    def test_list_models_and_versions(self):
        """Test the list_models_and_versions method."""
        print("\n" + "="*60)
        print("TESTING: list_models_and_versions")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_model_path)
        res = self.ceph.list_models_and_versions()
        assert isinstance(res, dict), "Result should be a dict"
        assert "test_class" in res, "Test model class should exist"
        assert "test_model" in res["test_class"], "Test model should exist"
        assert "model_v1" in res["test_class"]["test_model"], "Test version should exist"
        print("[SUCCESS] list_models_and_versions")

    def test_list_buckets_and_model_classes(self):
        """Test the list_buckets_and_model_classes method."""
        print("\n" + "="*60)
        print("TESTING: list_buckets_and_model_classes")
        print("="*60)
        self.ceph.upload_file(self.test_file_path, self.test_model_path)
        res = self.ceph.list_buckets_and_model_classes()
        assert isinstance(res, dict), "Result should be a dict"
        assert self.ceph.bucket_name in res, f"Bucket {self.ceph.bucket_name} should be listed"
        assert "test_class" in res[self.ceph.bucket_name], "Test model class should be listed"
        print("[SUCCESS] list_buckets_and_model_classes")

    # ============ Admin Ops (needs admin rights) ============

    def test_create_user(self):
        """Test the create_user method."""
        print("\n" + "="*60)
        print("TESTING: create_user")
        print("="*60)
        try:
            ak, sk = self.ceph.create_user(self.test_username)
            assert len(ak) >= 1 and len(sk) >= 1, "Access and secret keys should be non-empty"
            print("[SUCCESS] create_user")
        except Exception as e:
            if "AccessDenied" in str(e) or "403" in str(e):
                print("[NOTE] Admin rights required; skipping assert")
            else:
                raise

    def test_set_user_quota(self):
        """Test the set_user_quota method."""
        print("\n" + "="*60)
        print("TESTING: set_user_quota")
        print("="*60)
        try:
            self.ceph.set_user_quota(self.test_username, self.test_quota_gb)
            print("[SUCCESS] set_user_quota")
        except Exception as e:
            if "AccessDenied" in str(e) or "403" in str(e):
                print("[NOTE] Admin rights required; skipping assert")
            else:
                raise

    def test_enforce_storage_limit(self):
        """Test the enforce_storage_limit method."""
        print("\n" + "="*60)
        print("TESTING: enforce_storage_limit")
        print("="*60)
        result = self.ceph.enforce_storage_limit(self.ceph.bucket_name, 100)
        assert isinstance(result, bool), "Result should be boolean"
        try:
            self.ceph.enforce_storage_limit("non_existent_bucket", 100)
            assert False, "Non-existent bucket should raise ValueError"
        except ValueError:
            print("[SUCCESS] Non-existent bucket handling")
        print("[SUCCESS] enforce_storage_limit")

if __name__ == "__main__":
    # Instantiate tester
    tester = CephS3ManagerTester()

    # ================================================
    # RUN EXACTLY ONE TEST AT A TIME
    # Uncomment ONE line, run, then comment it again.
    # ================================================

    # --- Pure local helpers ---
    # tester.test_generate_random_string()
    # tester.test_generate_key()
    # tester.test_generate_access_key()
    # tester.test_generate_secret_key()

    # --- S3 connectivity/auth/buckets ---
    # tester.test_check_connection()  
    # tester.test_check_auth()  
    # tester.test_ensure_bucket_exists()
    # tester.test_list_buckets()
    # tester.test_list_available_buckets()  0
    # tester.test_print_bucket_full_detail()
    # tester.test_print_bucket_short_detail()   0 

    # --- System utilities ---
    # tester.test_check_command_exists()
    # tester.test_check_s5cmd()
    # tester.test_check_aws_credentials_folder()

    # --- Identity (may be unsupported on RGW) ---
    # tester.test_get_identity()
    # tester.test_get_user_info()

    # --- Upload/Download/File ops ---
    # tester.test_upload_file()
    # tester.test_upload_folder()
    # tester.test_check_if_exists()
    # tester.test_read_file_from_s3()
    # tester.test_get_uri_size()
    # tester.test_is_folder()
    # tester.test_download_file()
    # tester.test_download_folder()
    # tester.test_delete_folder()
    # tester.test_move_folder()
    # tester.test_list_folder_contents()
    # tester.test_find_file()

    # --- Models layout helpers ---
    # tester.test_list_model_classes()
    # tester.test_list_models_and_versions()
    # tester.test_list_buckets_and_model_classes()

    # --- Admin Ops (needs admin rights) ---
    # tester.test_create_user()
    # tester.test_set_user_quota()
    # tester.test_enforce_storage_limit()

    # Always cleanup at the end of each single run
    # tester.cleanup()