from setuptools import setup, find_packages

setup(
    name='viais-cli',  # Tên package: viais-cli
    version='0.1.0',  # Phiên bản, tăng dần khi update
    description='CLI tool for ViAIF pull-push service',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),  # Tự động tìm packages
    install_requires=[
        'click>=8.0',  # Dependencies
        # Thêm các lib khác nếu cần, ví dụ: 'minio' nếu dùng minio_handler
    ],
    entry_points={
        'console_scripts': [
            'viais-cli=cli:cli',  # Entry point: chạy 'viais-cli' sẽ gọi hàm cli() trong cli.py
        ],
    },
    python_requires='>=3.13',  # Phù hợp với env của bạn
)