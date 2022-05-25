import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, redirect, url_for, session, make_response, render_template, abort
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__, template_folder='template', static_url_path='/', static_folder='resource')
app.config['SECRET_KEY'] = os.urandom(24)

# 使用集成方式处理SQLALchemy
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://zihan:wang159357@101.43.202.135:3306/zihanblog?charset=utf8'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # true: 跟踪数据库的修改，及时发送信号
app.config["SQLALCHEMY_POOL_SIZE"] = 200
# 实例化db对象
db = SQLAlchemy(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error-404.html")

# 自定义异常处理方式, 装饰器参数500承接abort(500)抛出的异常状态码500, 处理函数必须接受一个e参数
@app.errorhandler(500)
def server_error(e):
    return render_template("error-500.html")


@app.route('/error')
def error_500():
    try:
        x = 10 / 0
        return x
    except:  # 当发生异常, 则主动抛出500状态码的异常
        return abort(500)

# 定义全局拦截器，实现自动登录
@app.before_request
def before():
    # 自动登录

    url = request.path
    pass_list = ['/user', '/login', '/logout']
    if url in pass_list or url.endswith('.js') or url.endswith('.jpg'):
        pass

    elif session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get("password")
        if username != None and password != None:
            user = Users()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role

# 通过自定义过滤器来重构truncate原生过滤器
def mytruncate(s, length, end='...'):
    count = 0;
    new = ''
    for c in s:
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
        if count > length:
            break
    return new + end
# 注册过滤器
app.jinja_env.filters.update(mytruncate=mytruncate)

# @app.route('/article')
# def article():
#     return render_template('article-base.html')

# 定义文章类型函数，供模板页面直接调用
# app_context_processor在flask中被称作上下文处理器，借助app_context_processor我们可以让所有
# 自定义变量在所有模板中全局可访问，如下面的代码，我们将email作为一个变量在所有模板中可见：
@app.context_processor
def gettype():
    type = {
        '1': '软件开发',
        '2': '软件测试',
        '3': '计算机基础知识',
        '4': '数据结构与算法',
        '5': '生活随笔',
        '6': '国家要闻'

    }
    return dict(article_type=type)



if __name__ == "__main__":
    from controller.index import *

    app.register_blueprint(index)

    from controller.user import *

    app.register_blueprint(user)

    from controller.article import *

    app.register_blueprint(article)

    from controller.favorite import *
    app.register_blueprint(favorite)

    from controller.comment import *
    app.register_blueprint(comment)

    from controller.ueditor import *
    app.register_blueprint(ueditor)

    # app.run(host="0.0.0.0", port=5000, debug=None, load_dotenv=True)
    app.run(debug=True)


