import os
import argparse
from pathlib import Path

import yaml
from framework.utils.common import snake_to_pascal
from config.settings import CONFIG_DIR, CASES_DIR, DATA_DIR


def create_yaml(app):
    """生成 YAML 文件"""
    os.makedirs(os.path.join(CONFIG_DIR, app), exist_ok=True)
    with open(os.path.join(CONFIG_DIR, app, "context.yaml"), 'w', encoding="utf-8") as f:
        yaml.dump({
            "dev": {
                "domain": "dev.example.com",
                "accounts": {
                    "admin": {
                        "username": "admin",
                        "password": "test"
                    }
                }
            }
        }, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    with open(os.path.join(CONFIG_DIR, app, "config.yaml"), 'w', encoding="utf-8") as f:
        yaml.dump({
            "dev": {
                "mysql": {
                    "host": None,
                    "username": None,
                    "password": None,
                    "port": 3306
                },
                "redis": {
                    "host": None,
                    "password": None,
                    "port": 6379
                }
            }
        }, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def create_test_case(app: str):
    os.makedirs(os.path.join(CASES_DIR, app), exist_ok=True)
    file_path = Path(os.path.join(CASES_DIR, app, "../__init__.py"))
    file_path.touch(exist_ok=True)
    content = f"""
from test_case import BaseTestCase


class TestUntitled(BaseTestCase):

    def test_untitled(self):
        # 发送请求
        self.request(app="{app}", account="admin", data=self.data)
        # 断言
        assert self.response.status_code == 200
        assert len(self.response.jsonpath("$.data.balances")) > 0"""
    with open(os.path.join(CASES_DIR, app, "test_untitled.py"), 'w', encoding="utf-8") as file:
        file.write(content)


def create_test_data(app):
    os.makedirs(os.path.join(DATA_DIR, app), exist_ok=True)

    with open(os.path.join(DATA_DIR, app, "test_untitled.yaml"), 'w', encoding="utf-8") as f:
        yaml.dump({
            "case_common": {
                "module": "功能模块名称",
                "describe": "测试场景描述",
                "scenarios": [
                    {
                        "scenario": {
                            "data": {
                                "tag_id": 1,
                                "user_id": 1
                            },
                            "exclude": [
                                "test_untitled"
                            ]
                        }
                    }
                ]
            },
            "test_untitled": {
                "title": "登录成功",
                "level": "p0",
                "request": {
                    "url": "/login",
                    "method": "post",
                    "json": {
                        "username": "Jerry",
                        "password": "${user_id}"
                    }
                },
                "extract": [
                    {
                        "id": "$.data.token"
                    }
                ]
            }
        }, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def create_app_session(app):
    content = f"""

class {snake_to_pascal(app)}Login(Login):

    def login(self, username, password, secret_key, **kwargs):
        client = HttpClient()
        # TODO 需要实现登录逻辑，将登录获取到的token添加到headers中
        token = None
        client.update_headers({{"token": token}})
        return client"""
    with open(os.path.join(CASES_DIR, "conftest.py"), "a", encoding="utf-8") as f:
        f.write(content)


def process_command_line_args():
    parser = argparse.ArgumentParser(description='startapp')
    parser.add_argument('app', type=str, help='创建应用')
    return parser.parse_args()


def main():
    args = process_command_line_args()
    app = args.app
    if not os.path.exists(os.path.join(DATA_DIR, app)):
        create_yaml(app)
        create_test_case(app)
        create_test_data(app)
        create_app_session(app)
        print(f"app {app}创建成功")
    else:
        print(f"app {app}已存在,未执行创建")


if __name__ == '__main__':
    main()
