import random
import time

from flask import session
from sqlalchemy import Table

from common.database import dbconnect

dbsession, md, DBase = dbconnect()


class Credit(DBase):
    __table__ = Table('credit', md, autoload=True)

    # 插入积分
    def insert_detail(self, types, target, credit):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        credit = Credit(userid=session.get('userid'), category=types, target=target,
                        credit=credit, createtime=now, updatetime=now)

        dbsession.add(credit)
        dbsession.commit()

    # 判断用户是否已经消耗了积分
    def check_payed_article(self, articleid):
        result = dbsession.query(Credit).filter_by(userid=session.get('userid'), target=articleid).all()
        if len(result) > 0:
            return True
        else:
            return False


