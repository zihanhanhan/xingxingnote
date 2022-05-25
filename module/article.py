import time

from flask import session

from common.database import dbconnect
from sqlalchemy import Table, func

from module.favorite import Favorite
from module.users import Users

dbsession, md, DBase = dbconnect()


class Article(DBase):
    __table__ = Table('article', md, autoload=True)

    # 查询所有文章
    # def fin

    # 根据id查询文章 (article, 'nickname')
    def find_by_id(self, articleid):
        row = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, \
                    Article.articleid == articleid).first()
        return row

    # 指定分页的limit和offset的参数值，同时与用户表做链接查询
    def find_limit_with_users(self, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    def get_total_count(self):
        count = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        return count

    # 根据文章类型获取文章
    def find_by_type(self, category, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.category == category) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 根据文章类型获取总数量
    def get_count_by_type(self, category):
        count = dbsession.query(Article).filter(Article.hide == 0,
                                                Article.drafted == 0,
                                                Article.checked == 1,
                                                Article.category == category).count()
        return count

    # 根据文章标题进行搜索
    def find_by_headline(self, headline, start, count):
        result = dbsession.query(Article, Users.nickname).join(Users, Users.userid == Article.userid) \
            .filter(Article.hide == 0,
                    Article.drafted == 0,
                    Article.checked == 1,
                    Article.headline.like('%' + headline + '%')) \
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 统计分页总数量
    def get_count_by_headline(self, headline):
        count = dbsession.query(Article).filter(Article.hide == 0,
                                                Article.drafted == 0,
                                                Article.checked == 1,
                                                Article.headline.like('%' + headline + '%')).count()
        return count

    # 最新文章
    def find_last_nine(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.articleid.desc()).limit(9).all()
        return result

    # 最多阅读
    def find_most_nine(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1) \
            .order_by(Article.readcount.desc()).limit(9).all()
        return result

    # 特别推荐  order by rand 随机出现
    def find_recommend_nine(self):
        result = dbsession.query(Article.articleid, Article.headline) \
            .filter(Article.hide == 0, Article.drafted == 0, Article.checked == 1, Article.recommended == 1) \
            .order_by(func.rand()).limit(9).all()
        return result

    # 一次性返回三个推荐数据
    def find_last_most_recommended(self):
        last = self.find_last_nine()
        most = self.find_most_nine()
        recommended = self.find_recommend_nine()
        # print(last, most, recommended)
        return last, most, recommended

    # 每阅读一次文章，阅读次数+1
    def update_read_count(self, articleid):
        article = dbsession.query(Article).filter_by(articleid=articleid).first()
        article.readcount += 1
        dbsession.commit()

    # 根据文章编号查询文章标题
    def find_headline_by_id(self, articleid):
        row = dbsession.query(Article.headline).filter_by(articleid=articleid).first()
        return row.headline

    # 获取当前文章的上一篇和下一篇
    def find_prev_next_by_id(self, articleid):
        dict = {}

        # 查询比当前编号小的最大一个
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0,
                                              Article.checked == 1, Article.articleid < articleid).order_by(
            Article.articleid.desc()).limit(1).first()

        # 如果当前已经是第一篇，上一篇也是当前文章
        if row is None:
            prev_id = articleid
        else:
            prev_id = row.articleid
        dict['prev_id'] = prev_id
        dict['prev_headline'] = self.find_headline_by_id(prev_id)

        # 查询比当前编号大的最小一个
        row = dbsession.query(Article).filter(Article.hide == 0, Article.drafted == 0,
                                              Article.checked == 1, Article.articleid > articleid).order_by(
            Article.articleid).limit(1).first()

        # 如果当前已经是第一篇，上一篇也是当前文章
        if row is None:
            next_id = articleid
        else:
            next_id = row.articleid
        dict['next_id'] = next_id
        dict['next_headline'] = self.find_headline_by_id(next_id)

        return dict

    # 发表或者回复评论后，为文章表字段replycount + 1
    def update_replycount(self, articleid):
        row = dbsession.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        dbsession.commit()

    # 插入一篇新的文章，草稿或投稿通过参数进行区分
    def insert_article(self, type, headline, content, thumbnail, credit, drafted=0, checked=1):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        userid = session.get('userid')
        # 其他字段在数据库中均已设置好默认值， 无需手工插入
        article = Article(userid=userid, category=type, headline=headline, content=content,
                          thumbnail=thumbnail, credit=credit, drafted=drafted, checked=checked,
                          createtime=now, updatetime=now)
        dbsession.add(article)
        dbsession.commit()

        return article.articleid  # 将文章编号返回，便于前端页面跳转

    # 判断该文章的积分是几
    # def how_many_credit(self, articleid):
    #     row = dbsession.query(Article).filter_by(articleid=articleid).first()
    #     print(row.credit)
    #     return row.credit

    # 用户中心：我的收藏页面  当前用户收藏的文章
    def favorite_article(self, start, count):
        result = dbsession.query(Article.articleid, Article.headline, Article.readcount)\
                .join(Favorite, Article.articleid == Favorite.articleid).filter(Favorite.canceled == 0)\
                .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 用户中心：我的收藏页面的分页操作
    def favorite_article_count(self):
        count = dbsession.query(Article).join(Favorite, Article.articleid == Favorite.articleid)\
            .filter(Favorite.canceled == 0).count()
        return count

    # 用户中心：我的文章页面 显示当前用户创作的所有文章
    def user_article(self, userid, start, count):
        result = dbsession.query(Article.articleid, Article.headline, Article.readcount)\
                    .join(Users, Article.userid == Users.userid)\
                    .filter(Article.userid == userid)\
                    .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    # 用户中心： 我的文章页面的分页操作
    def user_article_count(self, userid):
        count = dbsession.query(Article).join(Users, Article.userid == Users.userid)\
                .filter(Article.userid == userid, Article.hide == 0, Article.drafted == 0, Article.checked == 1).count()
        # print(count)
        return count


    # 删除文章操作
    def cancel_article(self, articleid):
        pass