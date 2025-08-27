from push_service import PushService
import os
import shutil
from utils.utils import *

from logs.log_handler import logger


if __name__ == "__main__":
    # src_folder = "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/template/input/identify-counting/ai-diplomat-service"
    # folder_path = (
    #     "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/push/ai-diplomat-service"
    # )
    # if os.path.exists(folder_path):
    #     shutil.rmtree(folder_path)
    # shutil.copytree(src_folder, folder_path, dirs_exist_ok=True)

    end_point = "minio-endpoint.viais.vision:9000"
    access_key = "viais"
    secret_key = "1234Qwer!"
    secure = False
    pull_service = PullService(
        end_point=end_point, access_key=access_key, secret_key=secret_key, secure=secure
    )

    dst_path = (
        "/home/ubuntu/personals/thiendn4/thiendn4/ViAIF/pull-push-service/output_multiple"
    )
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    else:
        os.remove(dst_path)
        os.makedirs(dst_path)
    list_values = read_package_file("./docs/package.json")
    package_name = list(list_values.keys())[0]  # "identify-counting"
    package_info = list_values[package_name]
    package_version = package_info.get("version")
    package_data = package_info.get("package_data", {})
    pull_full_package = package_info.get("pull_full_package", False)

    if not pull_full_package:
        for service_name, service_info in package_data.items():
            # Một số service có thêm service_data bên trong
            if "service_data" in service_info:
                for business_name, target_version in service_info["service_data"].items():
                    logger.debug(
                        f"Processing service: {service_name}, business: {business_name}, version: {target_version}"
                    )
                    pull_service.pull(
                        service_name=service_name,
                        package_name=package_name,
                        business_name=business_name,
                        target_version=target_version,
                        dst_path=dst_path,
                    )
            else:
                business_name = service_name
                target_version = service_info.get("version")
                logger.debug(
                    f"Processing service: {service_name}, version: {target_version}"
                )
                pull_service.pull_service(
                    service_name=service_name,
                    package_name=package_name,
                    business_name=business_name,
                    target_version=target_version,
                    dst_path=dst_path,
                )
    else:
        logger.debug(f"Pulling full package: {package_name}, version: {package_version}")
        pull_service.pull_package(
            package_name=package_name, package_version=package_version, dst_path=dst_path
        )
