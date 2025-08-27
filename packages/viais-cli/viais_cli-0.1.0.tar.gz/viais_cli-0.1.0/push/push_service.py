import os
import sys
current_directory = os.getcwd()
sys.path.append(current_directory)
from minio_storage.minio_handler import MinioHandler
import os
from utils.utils import (
    get_last_name,
    get_local_version_from_env,
    check_service_and_package,
    compare_versions,
    check_format_version,
    clear_service,
    clear_using_rules,
)
from logs.log_handler import logger
import shutil


class PushManager:
    def __init__(self, end_point, access_key, secret_key, secure):
        self.minio_handler = MinioHandler(
            endpoint=end_point,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = "encryption-source-test"
        self.package_bucket = "package-bucket"
        self.source = "source"
        self.docker = "docker"
        self.asset = "assets"

        # Kiểm tra kết nối MinIO
        if not self.check_minio_connection():
            return
        # Tạo bucket nếu chưa tồn tại
        try:
            self.minio_handler.make_bucket(self.bucket_name)
            logger.info(f"Buckets created or verified: {self.bucket_name}")
            self.minio_handler.make_bucket(self.package_bucket)
            logger.info(f"Buckets created or verified: {self.package_bucket}")
        except Exception as e:
            logger.error(f"Failed to create buckets: {e}")
            return

    def check_minio_connection(self):
        """Kiểm tra kết nối đến MinIO."""
        try:
            self.minio_handler.check_minio_connection()
            logger.info("MinIO connection successful")
            return True
        except Exception as e:
            logger.error(f"MinIO connection failed: {e}")
            return False
    
    # def check_get_name(self, folder_path):
    #     service_name = get_last_name(folder_path)
    #     if not service_name:
    #         message = "⚠️ Failed to extract service name"
    #         logger.error(message)
    #         # return False, message, False, "", None
    #         return False, message, True, "abc xxx", self.check_minio_connection
    #     else:
    #         message ="Extracted service name successfully"
    #         return True, message, False, "", None


    def push_service(self, folder_path, package_name, business_name):
        logger.info(
            f"Starting push for folder: {folder_path}, package: {package_name}, business: {business_name}"
        )
        # check folder in push --> status, message, response, message_response, function

        # Kiểm tra tên service
        service_name = get_last_name(folder_path)
        if not service_name:
            logger.error("⚠️ Failed to extract service name")
            return
        logger.info(f"Service name extracted: {service_name}")
        if service_name == "ai-xbusiness-service":
            folder_path = os.path.join(folder_path, package_name)

        # Kiểm tra đường dẫn folder_path
        if not os.path.exists(folder_path):
            logger.error(f"⚠️ Folder path not found: {folder_path}")
            return

        # Kiểm tra tên service và package
        if not check_service_and_package(service_name, package_name, business_name):
            return

        # Lấy phiên bản hiện tại từ .env
        docker_folder = os.path.join(folder_path, "docker")
        env_path = os.path.join(docker_folder, ".env")
        if not os.path.exists(env_path):
            logger.error(f"⚠️ .env file not found at {env_path}")
            return
        current_version = get_local_version_from_env(env_path)
        if not check_format_version(current_version):
            logger.error(f"⚠️ Invalid version format: {current_version}")
            return
        logger.debug(f"Current Version from .env: {current_version}")

        # Lấy phiên bản mới nhất trên MinIO
        lastest_version = self.minio_handler.get_lastest_version_on_minio(
            bucket_name=self.bucket_name, service_name=service_name
        )
        if not lastest_version:
            logger.info("No previous version found on MinIO.")
        else:
            logger.debug(f"Lastest version on MinIO: {lastest_version}")
            try:
                if compare_versions(current_version, lastest_version, "<="):
                    logger.debug(
                        f"Current version {current_version} is not newer than lastest version {lastest_version}. No push needed."
                    )
                    return
            except ValueError as e:
                return

        # Kiểm tra thư mục docker
        if not os.path.exists(docker_folder):
            logger.error(f"⚠️ Docker folder not found in {folder_path}")
            return

        # Define object name based on service name and package name
        if service_name == "ai-xbusiness-service":
            source_object_name = (
                f"{service_name}/{business_name}/{current_version}/{self.source}"
            )
            docker_object_name = (
                f"{service_name}/{business_name}/{current_version}/{self.docker}"
            )
            asset_object_name = (
                f"{service_name}/{business_name}/{current_version}/{self.asset}"
            )
        else:
            source_object_name = f"{service_name}/{current_version}/{self.source}"
            docker_object_name = f"{service_name}/{current_version}/{self.docker}"
            asset_object_name = f"{service_name}/{current_version}/{self.asset}"
        logger.info(f"Upload to: {f'{service_name}/{current_version}'}")

        # Đẩy thư mục docker lên MinIO
        try:
            self.minio_handler.upload_folder(
                self.bucket_name, docker_object_name, docker_folder
            )
            logger.info(f"Uploaded docker folder to {docker_object_name}")
        except Exception as e:
            logger.error(f"Failed to upload docker folder: {e}")
            return

        # Đẩy các file labels.txt lên MinIO
        try:
            asset_folder = os.path.join(folder_path, "assets")
            self.minio_handler.upload_folder(
                self.bucket_name,
                asset_object_name,
                asset_folder,
                file_condition="labels.txt",
            )
            logger.info(f"Uploaded assets folder to {asset_object_name}")
        except Exception as e:
            logger.error(f"Failed to upload asset folder: {e}")
            return

        # Xóa các file không cần thiết trước khi đẩy lên MinIO
        new_service_path = folder_path + "_temp"
        shutil.copytree(folder_path, new_service_path, dirs_exist_ok=True)
        # clear_using_rules(new_service_path, rules_file=os.path.join(folder_path, ".dockerignore"))
        clear_service(new_service_path, dry_run=False)
        self.minio_handler.upload_folder(
            self.bucket_name, source_object_name, new_service_path
        )
        shutil.rmtree(new_service_path)

    def push_package(self, folder_path, current_version):
        logger.info(f"Starting push for package: {folder_path}")

        # Kiểm tra tên service
        package_name = get_last_name(folder_path)
        if not package_name:
            logger.error("⚠️ Failed to extract package name")
            return

        # Kiểm tra đường dẫn folder_path
        if not os.path.exists(folder_path):
            logger.error(f"⚠️ Folder path not found: {folder_path}")
            return

        # Kiểm tra tên service và package
        if not check_service_and_package(package_name = package_name):
            return

        # Lấy phiên bản mới nhất trên MinIO
        lastest_version = self.minio_handler.get_lastest_version_on_minio(
            bucket_name=self.package_bucket, package_name=package_name
        )
        if not lastest_version:
            logger.info("No previous version found on MinIO.")
        else:
            logger.debug(f"Lastest version on MinIO: {lastest_version}")
            try:
                if compare_versions(current_version, lastest_version, "<="):
                    logger.debug(
                        f"Current version {current_version} is not newer than lastest version {lastest_version}. No push needed."
                    )
                    return
            except ValueError as e:
                return
        object_name = os.path.join(package_name, current_version)
        
        # Xóa các file không cần thiết trước khi đẩy lên MinIO
        new_service_path = folder_path + "_temp"
        shutil.copytree(folder_path, new_service_path, dirs_exist_ok=True)
        self.minio_handler.upload_folder(
            self.package_bucket, object_name, new_service_path
        )
        shutil.rmtree(new_service_path)
        logger.debug("Upload package successful")


if __name__ == "__main__":
    # src_folder = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/template/input/identify-counting"
    # folder_path = (
    #     "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull_and_push_service/input"
    # )
    # if os.path.exists(folder_path):
    #     shutil.rmtree(folder_path)
    # shutil.copytree(src_folder, folder_path, dirs_exist_ok=True)

    # # folder_path = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/input/ai-objects-service"
    # folder_path = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/input/ai-xbusiness-service"
    # # folder_path = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/input/ai-diplomat-service"
    # package_name = "identify-counting"
    # business_name = "identify-counting"
    # version = "1.0.0"
    # end_point = "minio-endpoint.viais.vision:9000"
    # access_key = "viais"
    # secret_key = "1234Qwer!"
    # secure = False

    # push_manager = PushManager(end_point, access_key, secret_key, secure)
    # push_manager.push(folder_path, package_name, business_name)

    folder_path = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/identify-counting"
    package_name = "identify-counting"
    business_name = "identify-counting"
    version = "1.0.1"
    end_point = "minio-endpoint.viais.vision:9000"
    access_key = "viais"
    secret_key = "1234Qwer!"
    secure = False

    push_manager = PushManager(end_point, access_key, secret_key, secure)
    push_manager.push_package(folder_path, version)
