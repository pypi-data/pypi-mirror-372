from setuptools import setup, find_packages

setup(
    name="pytest-api-framework-alpha",  # 包名（必须唯一）
    version="0.2.2",
    packages=find_packages(),
    author="alpha",
    author_email="",
    description="",
    python_requires='>=3.6',
    install_requires=[
        "allure-pytest==2.13.1",
        "allure-python-commons==2.13.1",
        "cn2an==0.5.19",
        "DBUtils==3.1.0",
        "Faker==18.3.2",
        "jsonpath==0.82",
        "pytest==7.2.2",
        "python-dotenv==1.0.1",
        "PyYAML==6.0.1",
        "python-box==7.2.0",
        "pycryptodome==3.21.0",
        "pyotp==2.9.0",
        "pytest-order==1.3.0",
        "PyMySQL==1.1.0",
        "redis==3.5.3",
        "requests==2.25.1",
        "requests-toolbelt==1.0.0",
        "retry==0.9.2",
        "dill==0.3.8"
    ]
)
