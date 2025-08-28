import json
from redis import Redis
from redis.exceptions import RedisError

from framework.utils.log_util import logger


class RedisDB(Redis):

    def __init__(self, host, port, password, db, max_connections=10):
        super(RedisDB, self).__init__()
        self.db = db
        self.max_connections = max_connections
        self.conn = Redis(
            host=host,
            port=port,
            password=password,
            db=self.db,
            decode_responses=True
        )

    def __del__(self):
        try:
            self.conn.close()
        except RedisError as e:
            logger.info(e)
            raise RedisError(f"redis close error>>>{e}")

    def set_string(self, name, value, ex=None):
        if ex:
            res = self.conn.set(name, value, ex)
            logger.info(f'set {name} {value} {ex} --->{res}')
        else:
            res = self.conn.set(name, value)
            logger.info(f'set {name} {value} --->{res}')
        if res:
            return res
        else:
            return False

    def set_hash(self, name, value):
        res = self.conn.hmset(name, value)
        logger.info(f'hmset {name} {value} --->{res}')
        if res:
            return res
        else:
            return False

    def set_list(self, name, value):
        """
        value可以是字典；列表[字典]；列表[数字]；列表[字符串];空字典;空列表;空字符串；None
        :param name:
        :param value:
        :return:
        """

        if value:
            if isinstance(value, dict):
                self.push(name, value)
            elif isinstance(value, list):
                if isinstance(value[0], dict):
                    value = [json.dumps(item, ensure_ascii=False) for item in value]
                    self.conn.lpush(name, *value)
                elif isinstance(value[0], (int, str)):
                    self.conn.lpush(name, json.dumps(value, ensure_ascii=False))
                else:
                    self.conn.lpush(name, str(value))
            else:
                self.conn.lpush(name, value)
        else:
            self.conn.lpush(name, json.dumps(value))

    def get_string(self, name):
        res = self.conn.get(name)
        logger.info(f'get {name}')
        if res:
            return res
        else:
            return None

    def get_hash(self, name):
        res = self.conn.hgetall(name)
        logger.info(f'hgetall {name}')
        if res:
            return res
        else:
            return None

    def get_list(self, name):
        res = self.conn.lrange(name, 0, -1)
        if res:
            return [json.loads(item) for item in res]

    def get_ttl(self, name):
        res = self.conn.ttl(name)
        logger.info(f'ttl {name} ---> {res}')
        if res:
            return res
        else:
            return None

    def set_ttl(self, name, time):
        res = self.conn.expire(name, time)
        logger.info(f'expire {name} {time} ---> {res}')
        if res:
            return res
        else:
            return False

    def exists(self, name):
        res = self.conn.exists(name)
        logger.info(f'exists {name} ---> {res}')
        if res:
            return True
        else:
            return False

    def delete(self, name):
        res = self.conn.delete(name)
        logger.info(f'delete {name} ---> {res}')
        if res:
            return True
        else:
            return False

    def push(self, name, value):
        """
        通过list实现队列，从左侧推消息,消息体只能字典
        :param name:
        :param value:
        :return:
        """
        res = self.conn.lpush(name, json.dumps(value, ensure_ascii=False))
        logger.info(f'lpush {name} ---> {value}')
        if res:
            return True
        else:
            return False


if __name__ == '__main__':
    redis = RedisDB(db=0)
