import os

import platform
from framework.utils.log_util import logger
from framework.global_attribute import CONTEXT
from config.settings import ALLURE_DIR, ALLURE_REPORT_DIR, ALLURE_RESULTS_DIR, ALLURE_ENV_PROPERTIES


def generate_report():
    set_allure_environment()
    if platform.platform() == "Linux":
        return

    try:
        cmd = f"{ALLURE_DIR} generate {ALLURE_RESULTS_DIR} -o {ALLURE_REPORT_DIR} --clean"
        os.system(cmd)
    except Exception as e:
        logger.error(f"生成allure测试报告异常:{e}")


def set_allure_environment():
    """生成allure的环境信息"""
    environment = list()
    pl = platform.platform()
    pl = pl[:pl.index("-")]
    environment.append(f"Platform={pl}\n")
    python_version = platform.python_version()
    environment.append(f"Python={python_version}\n")
    allure_version = "2.13.1"
    environment.append(f"Allure={allure_version}\n")
    environment.append(f"Env={CONTEXT.env}\n")
    environment.append(f"App={CONTEXT.app}\n")

    # with open(ALLURE_ENV_PROPERTIES, "w") as f:
    #     f.writelines(environment)
