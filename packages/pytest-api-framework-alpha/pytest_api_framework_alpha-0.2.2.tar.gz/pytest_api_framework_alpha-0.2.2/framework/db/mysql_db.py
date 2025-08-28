import json
from datetime import datetime
from decimal import Decimal

import retry
import pymysql

from dbutils.pooled_db import PooledDB
from framework.utils.log_util import logger


class MysqlDB(object):

    def __init__(self, host, username, password, port, db):
        self.__create_pool(host, username, password, port, db)

    @retry.retry(tries=5, delay=3)
    def __create_pool(self, host, username, password, port, db):
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=1,
            mincached=1,
            maxcached=2,
            blocking=True,
            maxusage=None,
            setsession=[],
            ping=0,
            host=host,
            user=username,
            password=password,
            db=db,
            port=port,
            charset='utf8'
        )

    def query(self, sql):
        """查询，返回结果"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql)
            logger.info(f"执行SQL: {sql}")
            result = cursor.fetchall()
            if len(result) == 1:
                result = result[0]
            elif len(result) == 0:
                result = None
            if isinstance(result, dict) or isinstance(result, list):
                logger.info(f"SQL执行结果: {json.dumps(result, default=MysqlDB.custom_serializer)}")
            else:
                logger.info(f"SQL执行结果: {result}")
            return result
        except pymysql.MySQLError as e:
            logger.error(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    def insert(self, sql):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            result = cursor.execute(sql)
            connection.commit()
            inserted_id = cursor.lastrowid
            print(f"插入的记录的主键ID: {inserted_id}")
            return inserted_id
        except pymysql.MySQLError as e:
            print(e)
            return None
        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    def execute(self, sql):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            result = cursor.execute(sql)
            logger.info(f"执行SQL: {sql}")
            connection.commit()
            logger.info(f"SQL执行结果: {result}")
            return result
        except pymysql.MySQLError as e:
            logger.error(f"Error executing execute: {e}")
            return None
        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    def executemany(self, sql, data):
        """修改，新增，删除"""
        connection = self.pool.connection()  # 获取一个连接
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.executemany(sql, data)
            logger.info(f"执行SQL: {sql}")
            connection.commit()
            logger.info(f"{cursor.rowcount} records inserted.")
        except pymysql.MySQLError as e:
            logger.error(f"Error executing execute: {e}")
            return None
        finally:
            cursor.close()  # 关闭游标
            connection.close()  # 将连接返回到连接池

    @staticmethod
    def custom_serializer(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # 转换时间格式
        elif isinstance(obj, Decimal):
            return float(obj)  # 转换 Decimal 为 float
        raise TypeError(f"Type {type(obj)} not serializable")
