import os
import sys
current_directory = os.getcwd()
sys.path.append(current_directory)
from minio_storage.minio_handler import MinioHandler
import shutil
from utils.utils import *
from logs.log_handler import logger
import time


class PullManager:
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
        self.assets = "assets"
        # Kiểm tra kết nối MinIO và bucket
        self.minio_handler.check_minio_connection()
        # Kiểm tra bucket có tồn tại
        self.check_bucket_exists()

    def check_bucket_exists(self):
        """Check if the bucket exists in MinIO"""
        all_buckets = self.minio_handler.get_all_buckets()
        if self.bucket_name not in all_buckets:
            logger.info(f"Bucket '{self.bucket_name}' does not exist.")
            return False
        return True

    def pull_service(
        self, service_name, package_name, business_name, target_version, dst_path
    ):
        logger.info(
            f"Starting pull for service: {service_name}, package: {package_name}, business: {business_name}"
        )
        # Kiểm tra và tạo thư mục đích nếu không tồn tại
        if not os.path.exists(dst_path):
            if (
                input(
                    f"Thư mục {dst_path} không tồn tại. Bạn có muốn tạo nó không? (y/n): "
                ).lower()
                != "y"
            ):
                logger.debug("Không tạo thư mục. Kết thúc chương trình.")
                exit(0)
            os.makedirs(dst_path)
        accept_pull_source = True
        accept_pull_docker = True
        accept_pull_assets = True
        service_dst_path = os.path.join(dst_path, service_name)

        # Kiểm tra xem service và package có hợp lệ không
        check_service_and_package(
            service_name=service_name,
            package_name=package_name,
            business_name=business_name,
        )

        if target_version == "lastest":
            target_version = self.minio_handler.get_lastest_version_on_minio(
                bucket_name=self.bucket_name, service_name=service_name
            )

        logger.debug("Check on Minio...")
        # Tạo object_name tùy theo loại service
        if service_name == "ai-xbusiness-service":
            source_object_name = (
                f"{service_name}/{business_name}/{target_version}/{self.source}"
            )
            docker_object_name = (
                f"{service_name}/{business_name}/{target_version}/{self.docker}"
            )
            assets_object_name = (
                f"{service_name}/{business_name}/{target_version}/{self.assets}"
            )
        else:
            source_object_name = f"{service_name}/{target_version}/{self.source}"
            docker_object_name = f"{service_name}/{target_version}/{self.docker}"
            assets_object_name = f"{service_name}/{target_version}/{self.assets}"

        # Kiểm tra xem service, package và version có tồn tại trên MinIO không
        self.minio_handler.check_service_exists_on_minio(self.bucket_name, service_name)

        self.minio_handler.check_package_exists_on_minio(
            self.bucket_name, service_name, business_name
        )

        exists = self.minio_handler.check_version_exists_on_minio(
            self.bucket_name, service_name, target_version
        )
        if exists:
            logger.debug(
                f"Version '{target_version}' TỒN TẠI trong service '{service_name}' trên Minio."
            )
        else:
            logger.warning(
                f"Version '{target_version}' KHÔNG tồn tại trong service '{service_name}' trên Minio. Dừng pull."
            )
            all_version = self.minio_handler.get_all_versions_in_service(
                self.bucket_name, service_name
            )
            logger.debug(
                f"Tất cả các phiên bản trong service {service_name}: {all_version}"
            )
            return

        version_object_name = (
            f"{service_name}/{business_name}/{target_version}"
            if service_name == "ai-xbusiness-service"
            else f"{service_name}/{target_version}"
        )
        exists_folders = self.minio_handler.check_required_folders_exist_on_minio(
            self.bucket_name, version_object_name
        )
        # logger.info(f"Tồn tại trên MinIO: {exists_folders}")
        if not all(exists_folders.values()):
            logger.warning(
                f"Thiếu folder trên MinIO: {', '.join([k for k, v in exists_folders.items() if not v])}"
            )
            # return

        if target_version is not None:
            lastest_version = self.minio_handler.get_lastest_version_on_minio(
                bucket_name=self.bucket_name, service_name=service_name
            )
            logger.info(f"Latest target_version on MinIO: {lastest_version}")

            # So sánh phiên bản
            result_compare = compare_versions(
                current_version=target_version,
                lastest_version=lastest_version,
                operator="<=",
            )
            if not result_compare:
                logger.warning(
                    f"Current target_version {target_version} is not available on minio. Lastest version on minio: {lastest_version}. Stop pulling."
                )
                return
        logger.info("Đã kiểm tra trên Minio")

        logger.info("Kiểm tra trên Local...")
        if os.path.exists(service_dst_path):
            # Nếu thư mục đã tồn tại → hỏi user
            user_choice_service = check_local_service_exists(
                dst_path, service_name, business_name
            )
            if user_choice_service == "Y":
                logger.debug(f"Tiếp tục tải và ghi đè service.")
            elif user_choice_service == "N":
                logger.debug(f"Bỏ qua tải service.")
                accept_pull_source = False

        assets_dst_path = os.path.join(dst_path, "assets")
        service_assets_dst_path = os.path.join(assets_dst_path, service_name)
        # target_version = None
        if os.path.exists(service_assets_dst_path):
            # Nếu thư mục đã tồn tại → hỏi user
            user_choice_service = check_local_service_exists(
                assets_dst_path, service_name, business_name
            )

            if user_choice_service == "Y":
                logger.debug(f"Tiếp tục tải và ghi đè service.")
            elif user_choice_service == "N":
                logger.debug(f"Bỏ qua tải service.")
                accept_pull_assets = False

        docker_dst_path = os.path.join(dst_path, "docker")
        service_docker_dst_path = os.path.join(docker_dst_path, service_name)
        if os.path.exists(service_docker_dst_path):
            # Nếu thư mục đã tồn tại → hỏi user
            user_choice_service = check_local_service_exists(
                docker_dst_path, service_name, business_name
            )

            if user_choice_service == "Y":
                logger.debug(f"Tiếp tục tải và ghi đè docker.")

            elif user_choice_service == "N":
                logger.debug(f"Bỏ qua tải service.")
                accept_pull_docker = False

            if service_name == "ai-xbusiness-service":
                env_path = os.path.join(
                    dst_path, "docker", service_name, business_name, ".env"
                )
            else:
                env_path = os.path.join(dst_path, "docker", service_name, ".env")
            current_version = get_version_from_env(env_path)
            if current_version is None:
                logger.error(f"⚠️ Không tìm thấy VERSION trong file .env: {env_path}")
                return
            result_compare = compare_versions(
                target_version, current_version, operator="<="
            )

            if result_compare:
                logger.info(
                    f"Current target_version {target_version} is not newer than latest target_version {current_version}. No pull needed."
                )
                self.minio_handler.get_lastest_version_on_minio(
                    bucket_name=self.bucket_name, service_name=service_name
                )
                return

        logger.info(f"Đã kiểm tra trên Local")

        if accept_pull_docker or accept_pull_source or accept_pull_assets:

            # Tạo thư mục assets và docker nếu chưa có
            create_folders_assets_docker(dst_path)

            if accept_pull_source:
                self.minio_handler.download_folder(
                    self.bucket_name, source_object_name, dst_path
                )
                move_version_folder_to_parent(dst_path, source_object_name)
            if accept_pull_docker:
                self.minio_handler.download_folder(
                    self.bucket_name, docker_object_name, docker_dst_path
                )
                move_version_folder_to_parent(docker_dst_path, docker_object_name)
            if accept_pull_assets:
                logger.debug(f"Downloading assets from MinIO: {assets_object_name}")
                self.minio_handler.download_folder(
                    self.bucket_name, assets_object_name, assets_dst_path
                )
                move_version_folder_to_parent(assets_dst_path, assets_object_name)
                move_up_one_level(assets_dst_path)

            # Sinh Makefile
            generate_flat_makefile_for_docker(docker_dst_path)

            # Đổi biến ENV sang PROD
            if service_name == "ai-xbusiness-service":
                env_path = os.path.join(
                    dst_path, "docker", service_name, business_name, ".env"
                )
            else:
                env_path = os.path.join(dst_path, "docker", service_name, ".env")
            rename_env_to_prod(env_path)

            print(f"Done pulling service {service_name} from MinIO.")
    
    def pull_package(
        self, package_name, target_version, dst_path
    ):
        logger.info(
            f"Starting pull for package: {service_name}, package: {package_name}, business: {business_name}"
        )
        # Kiểm tra và tạo thư mục đích nếu không tồn tại
        if not os.path.exists(dst_path):
            if (
                input(
                    f"Thư mục {dst_path} không tồn tại. Bạn có muốn tạo nó không? (y/n): "
                ).lower()
                != "y"
            ):
                logger.debug("Không tạo thư mục. Kết thúc chương trình.")
                exit(0)
            os.makedirs(dst_path)
        accept_pull = True
        package_dst_path = os.path.join(dst_path, package_name)

        # Kiểm tra xem service và package có hợp lệ không
        check_service_and_package(
            package_name=package_name
        )

        if target_version == "lastest":
            target_version = self.minio_handler.get_lastest_version_on_minio(
                bucket_name=self.package_bucket, service_name=package_name
            )

        logger.debug("Check on Minio...")
        # Tạo object_name tùy theo loại service
        object_name = os.path.join(package_name, target_version)

        # # Kiểm tra xem service, package và version có tồn tại trên MinIO không
        # self.minio_handler.check_service_exists_on_minio(self.package_bucket, package_name)

        self.minio_handler.check_package_exists_on_minio(
            self.package_bucket, package_name
        )

        exists = self.minio_handler.check_version_exists_on_minio(
            self.package_bucket, package_name, target_version
        )
        if exists:
            logger.debug(
                f"Version '{target_version}' TỒN TẠI trong service '{service_name}' trên Minio."
            )
        else:
            logger.warning(
                f"Version '{target_version}' KHÔNG tồn tại trong service '{service_name}' trên Minio. Dừng pull."
            )
            all_version = self.minio_handler.get_all_versions_in_service(
                self.package_bucket, package_name
            )
            logger.debug(
                f"Tất cả các phiên bản trong service {service_name}: {all_version}"
            )
            return

        if target_version is not None:
            lastest_version = self.minio_handler.get_lastest_version_on_minio(
                bucket_name=self.package_bucket, service_name=package_name
            )
            logger.info(f"Latest target_version on MinIO: {lastest_version}")

            # So sánh phiên bản
            result_compare = compare_versions(
                current_version=target_version,
                lastest_version=lastest_version,
                operator="<=",
            )
            if not result_compare:
                logger.warning(
                    f"Current target_version {target_version} is not available on minio. Lastest version on minio: {lastest_version}. Stop pulling."
                )
                return
        logger.info("Đã kiểm tra trên Minio")

        logger.info("Kiểm tra trên Local...")
        if os.path.exists(package_dst_path):
            # Nếu thư mục đã tồn tại → hỏi user
            user_choice_package = check_local_service_exists(
                dst_path, package_name, business_name
            )
            if user_choice_package == "Y":
                logger.debug(f"Tiếp tục tải và ghi đè package.")
            elif user_choice_package == "N":
                logger.debug(f"Bỏ qua tải package.")
                accept_pull = False

        logger.info(f"Đã kiểm tra trên Local")

        if accept_pull:

            self.minio_handler.download_folder(
                self.package_bucket, object_name, package_dst_path
            )
            move_version_folder_to_parent(package_dst_path, object_name)
            print(f"Done pulling service {service_name} from MinIO.")


if __name__ == "__main__":
    service_name = "ai-objects-service"
    # service_name = "ai-diplomat-service"
    # service_name = "ai-xbusiness-service"
    package_name = "identify-counting"
    business_name = "identify-counting"
    target_version = "1.0.1"
    end_point = "minio-endpoint.viais.vision:9000"
    access_key = "viais"
    secret_key = "1234Qwer!"
    secure = False

    dst_path = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/output"
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    # folder_exits = os.path.join(dst_path, service_name)
    # if os.path.exists(folder_exits):
    #     delete_folder = input(f"Thư mục {folder_exits} đã tồn tại. Bạn có muốn xóa nó không? (y/n): ").lower()
    #     if delete_folder == 'y':
    #         shutil.rmtree(folder_exits)
    #         logger.debug(f"Đã xóa thư mục {folder_exits}.")
    # time.sleep(10)

    # folder_exits = os.path.join(docker_dst_path, service_name)
    # if os.path.exists(folder_exits):
    #     delete_folder = input(f"Thư mục {folder_exits} đã tồn tại. Bạn có muốn xóa nó không? (y/n): ").lower()
    #     if delete_folder == 'y':
    #         shutil.rmtree(folder_exits)
    #         logger.debug(f"Đã xóa thư mục {folder_exits}.")

    # Khoi tao PullManager
    pull_manager = PullManager(
        end_point=end_point, access_key=access_key, secret_key=secret_key, secure=secure
    )

    
    # pull_manager.pull_service(
    #     service_name=service_name,
    #     package_name=package_name,
    #     business_name=business_name,
    #     target_version=target_version,
    #     dst_path=dst_path,
    # )
    pull_manager.pull_package(
        package_name=package_name,
        target_version=target_version,
        dst_path=dst_path,
    )
