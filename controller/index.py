import hashlib
import math
import os

from flask import Blueprint, render_template, abort, jsonify, json, session, request

from module.article import Article
from module.comment import Comment
from module.users import Users

index = Blueprint("index", __name__)


# @index.route('/')
# def home():
#     article = Article()
#     result = article.find_limit_with_users(0, 10)
#     total = math.ceil(article.get_total_count() / 10)
#
#     last, most, recommended = article.find_last_most_recommended()
#
#     return render_template('index-base.html', result=result, page=1, total=total,
#                               last=last, most=most, recommended=recommended)  # 第一个result是模板页面读取的，第二个是控制器的局部变量

@index.route('/')
def home():
    # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
    if os.path.exists('./template/index-static/index-1.html'):
        return render_template('index-static/index-1.html')  # 第一个result是模板页面读取的，第二个是控制器的局部变量
    # 下述代码跟之前版本保持不变，正常查询数据库
    article = Article()
    result = article.find_limit_with_users(0, 10)
    total = math.ceil(article.get_total_count() / 10)
    content = render_template('index-base.html', result=result, page=1, total=total)  # 第一个result是模板页面读取的，第二个是控制器的局部变量

    with open('./template/index-static/index-1.html', mode='w', encoding='utf-8') as file:
        file.write(content)

    return content


# 分页操作
@index.route('/page-<int:page>')
def paginate(page):
    # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
    if os.path.exists(f'./template/index-static/index-{page}.html'):
        return render_template(f'index-static/index-{page}.html')
    # 下述代码跟之前版本保持不变，正常查询数据库
    start = (page - 1) * 10
    article = Article()
    result = article.find_limit_with_users(start, 10)
    total = math.ceil(article.get_total_count() / 10)
    content = render_template('index-base.html', result=result, page=page,
                              total=total)  # 第一个result是模板页面读取的，第二个是控制器的局部变量

    with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
        file.write(content)

    return content


# @index.route('/page-<int:page>')
# def paginate(page):
#     start = (page - 1) * 10
#     article = Article()
#     result = article.find_limit_with_users(start, 10)
#     total = math.ceil(article.get_total_count() / 10)
#     return render_template('index-base.html', result=result, page=page, total=total)


@index.route('/type/<category>-<int:page>')
def classify(category, page):
    article = Article()
    start = (page - 1) * 10
    result = article.find_by_type(category, start, 10)
    total = math.ceil(article.get_count_by_type(category) / 10)
    return render_template('type.html', result=result, page=page, total=total, type=int(category))


@index.route('/search/<int:page>-<keyword>')
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 10:
        abort(404)

    start = (page - 1) * 10
    article = Article()
    result = article.find_by_headline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)

    return render_template('search.html', result=result, page=page, total=total, keyword=keyword)


@index.route('/recommend')
def recommend():
    # dic = {"a": 1, "b": 2, "c": "你好"}
    dic = [(128, '利用ThinkPHP框架开发Web应用系统'), (127, '测试用例设计（一）'), (126, '测试用例设计（一）'), (125, '软件测试六大类型（二）'),
           (124, '软件测试六大类型（一）'), (123, '测试与开发团队该如何配合？'), (122, '预备知识：软件工程与软件研发'), (121, 'Appium核心应用（四）'),
           (120, 'Appium核心应用（三）')]
    dic2 = [(128, '利用ThinkPHP框架开发Web应用系统'), (127, '测试用例设计（一）'), (126, '测试用例设计（一）'), (125, '软件测试六大类型（二）'),
            (124, '软件测试六大类型（一）'), (123, '测试与开发团队该如何配合？'), (122, '预备知识：软件工程与软件研发'), (121, 'Appium核心应用（四）'),
            (120, 'Appium核心应用（三）')]
    dic3 = [(128, '利用ThinkPHP框架开发Web应用系统'), (127, '测试用例设计（一）'), (126, '测试用例设计（一）'), (125, '软件测试六大类型（二）'),
            (124, '软件测试六大类型（一）'), (123, '测试与开发团队该如何配合？'), (122, '预备知识：软件工程与软件研发'), (121, 'Appium核心应用（四）'),
            (120, 'Appium核心应用（三）')]
    data = [dic, dic2, dic3]
    article = Article()
    last, most, recommended = article.find_last_most_recommended()
    # for i in list1:
    #     print(type(i[0]))
    # steps.append(step)
    # for item in list:
    #     data.append(list)
    # print(type(list1[0]))
    # print(last, most, recommended)
    return jsonify([list(i) for i in last], [list(i) for i in most], [list(i) for i in recommended])


# 静态化处理
@index.route('/static')
def all_static():
    pagesize = 10
    article = Article()
    # 先计算一共有多少页，处理逻辑与分页接口一致
    total = math.ceil(article.get_total_count() / pagesize)
    # 遍历每一页的内容，从数据库中查询出来，渲染到对应页面
    for page in range(1, total + 1):
        start = (page - 1) * pagesize
        result = article.find_limit_with_users(start, pagesize)

        # 将当前页面正常渲染，但不响应给前端，而是将渲染后的内容写入静态文件
        content = render_template('index-base.html', result=result, page=page, total=total)

        # 将渲染后的内容写入静态文件，其实content本身就是标准的HTML页面
        with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
            file.write(content)

    return '文章列表页面分页静态化处理完成'  # 最后简单响应给前面一个提示信息


@index.route('/ucenter-<int:page>')
def ucenter(page):
    article = Article()
    start = (page - 1) * 10
    result = article.favorite_article(start, 10)
    total = math.ceil(article.favorite_article_count() / 10)

    return render_template('user.html', result=result, page=page, total=total)


@index.route('/ucenter/article-<int:page>')
def user_article(page):
    article = Article()
    start = (page - 1) * 10
    userid = session.get('userid')
    result = article.user_article(userid, start, 10)
    total = math.ceil(article.user_article_count(userid) / 10)
    # print(total)

    return render_template('user-article.html', result=result, page=page, total=total)

# @index.route('/page-<int:page>')
# def paginate(page):
#     start = (page - 1) * 10
#     article = Article()
#     result = article.find_limit_with_users(start, 10)
#     total = math.ceil(article.get_total_count() / 10)
#     return render_template('index-base.html', result=result, page=page, total=total)

@index.route('/ucenter/comment-<int:page>')
def user_comment(page):
    comment = Comment()
    start = (page - 1) * 10
    userid = session.get('userid')
    result = comment.user_comment(userid, start, 10)
    total = math.ceil(comment.user_comment_count(userid) / 10)
    return render_template('user-comment.html', page=page, total=total, result=result)
    # return 'ok'

# 个人积分版块
@index.route('/ucenter/credit')
def user_credit():
    user = Users()
    credit = user.find_user_credit()

    return render_template('user-credit.html', credit=credit)