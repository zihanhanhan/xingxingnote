import redis

from common.utility import model_list
from module.users import Users


def redis_connect():
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True, db=0)
    red = redis.Redis(connection_pool=pool)
    return red


# def redis_mysql_string():
#     from common.database import dbconnect
#
#     red = redis_connect()  # 连接到Redis服务器
#
#     # 获取数据库连接信息
#     dbsession, md, DBase = dbconnect()
#
#     # 查询users表里的所有数据，并将其转换为json
#     result = dbsession.query(Users).all()
#     json = model_list(result)
#
#     red.set('users', str(json))  # 将整张表的数据保存成json字符串

def redis_mysql_hash():
    from common.database import dbconnect

    red = redis_connect()  # 连接到Redis服务器

    # 获取数据库连接信息
    dbsession, md, DBase = dbconnect()

    # 查询users表里的所有数据，并将其转换为json
    result = dbsession.query(Users).all()
    user_list = model_list(result)
    for user in user_list:
        red.hset('users_hash', user['username'], str(user))


if __name__ == "__main__":
    redis_mysql_hash()
