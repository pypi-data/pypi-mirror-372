import json
import argparse
import datetime
import traceback
from pathlib import Path
from framework.db.mysql_db import MysqlDB
from config.settings import DATABASE_HOST, DATABASE_PASSWORD, DATABASE_DB, DATABASE_USERNAME, DATABASE_PORT


def timestamp_to_datetime_str(timestamp):
    # 将时间戳转换为 datetime 对象
    dt = datetime.datetime.fromtimestamp(timestamp)
    # 将 datetime 对象格式化为指定格式的字符串
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


if __name__ == '__main__':
    print('调用report脚本')
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="演示如何使用 argparse 获取命令行参数")
    # 添加位置参数
    parser.add_argument('--task', help="输入任务的名字", required=True)
    # 添加可选参数
    parser.add_argument('--buildnum', type=int, help="输入构建次数", required=True)
    parser.add_argument('--allure_result', type=str, help="allure_result路径", required=True)

    # 解析命令行参数
    args = parser.parse_args()
    if not args.task:
        exit(400)
    print(f"task, {args.task}!")
    taskName = args.task

    if not args.buildnum:
        exit(400)
    print(f"buildnum, {args.buildnum}!")
    buildNum = args.buildnum

    if not args.allure_result:
        exit(400)
    print(f"allure_result_path, {args.allure_result}!")
    allure_result_path = args.allure_result

    # 初始化数据库连接
    print('初始化数据库连接')
    mysqlDB = MysqlDB(
        host=DATABASE_HOST,
        username=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        port=DATABASE_PORT,
        db=DATABASE_DB
    )

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    task_id = mysqlDB.insert(
        f"INSERT INTO tbl_task (name,last_run_time,buildnum) VALUES ('{taskName}','{formatted_time}','{buildNum}')")
    print(f'{task_id}')

    # 获取所有‘result.json‘结尾的文件
    print('获取所有‘*result.json‘结尾的文件')
    folder = Path(allure_result_path)
    all = list(folder.rglob('*result.json'))
    print(f'files count: {len(all)}')

    for file_path in all:
        try:
            # 打开 JSON 文件
            with open(file_path, 'r', encoding='utf-8') as file:
                # 解析 JSON 文件内容
                data = json.load(file)
                # 示例：访问解析后的数据
                if 'fullName' in data:
                    print(f"fullName: {data['fullName']}")
                if 'testCaseId' in data:
                    print(f"testCaseId: {data['testCaseId']}")
                if 'start' in data:
                    print(f"start: {data['start']}")
                if 'stop' in data:
                    print(f"stop: {data['stop']}")
                if 'uuid' in data:
                    print(f"uuid: {data['uuid']}")
                if 'status' in data:
                    print(f"status: {data['status']}")

                if 'name' in data:
                    print(f"name: {data['name']}")

                    if 'statusDetails' in data and data['statusDetails'] is not None:
                        mysqlDB.execute(
                            f"INSERT INTO tbl_test_case (test_case_id,status,name,starttime,stoptime,uuid,task_id,message) VALUES ('{data['testCaseId']}','{data['status']}','{data['name']}',{data['start']},{data['stop']},'{data['uuid']}',{task_id},'{str(data['statusDetails'])}')")
                    else:
                        mysqlDB.execute(
                            f"INSERT INTO tbl_test_case (test_case_id,status,name,starttime,stoptime,uuid,task_id) VALUES ('{data['testCaseId']}','{data['status']}','{data['name']}',{data['start']},{data['stop']},'{data['uuid']}',{task_id})")

        except FileNotFoundError:
            print("错误: 文件未找到，请检查文件路径是否正确。")
        except json.JSONDecodeError:
            print("错误: JSON 解析出错，请检查文件内容格式是否正确。")
        except Exception as e:
            print(f"发生未知错误: {e}")
            traceback.print_exc()
