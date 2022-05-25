import hashlib
import re

from flask import Blueprint, make_response, session, request, redirect, url_for, jsonify
from common.utility import ImageCode, gen_email_code, send_email
from module.credit import Credit
from module.users import Users

user = Blueprint("user", __name__)


@user.route('/vcode')
def vcode():
    code, bstring = ImageCode().get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    session['vcode'] = code.lower()
    return response


@user.route('/ecode', methods=['POST'])
def ecode():
    email = request.form.get('email')
    if not re.match('.+@.+\..+', email):
        return 'email-invalid'

    code = gen_email_code()
    try:
        send_email(email, code)
        session['ecode'] = code  # 将邮箱验证码保存在session中
        return 'send-pass'
    except:
        return 'send-fail'


@user.route('/user', methods=['POST'])
def register():
    user = Users()
    username = request.form.get('username')
    password = request.form.get('password')
    ecode = request.form.get('ecode')
    print(type(ecode))
    print(type(session.get('ecode')))
    print(ecode, session.get('ecode'))
    print(username)
    print(password)
    # 校验验证码是否正确
    if ecode != session.get('ecode'):

        return 'ecode-error'

    # 验证码邮箱地址的正确性和密码有效性
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalid'

    # 验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return 'user-repeated'

    else:
        # 实现注册
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.do_register(username, password)
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        # print(username, session['username'])
        # print(password, session['password'])
        # 更新积分详情表
        Credit().insert_detail(types='用户注册', target='0', credit=50)
        return 'reg-pass'


@user.route('/login', methods=['POST'])
def login():
    user = Users()
    username = request.form.get('username')
    password = request.form.get('password')
    vcode = request.form.get('vcode').lower()
    # print(vcode,session.get('vcode'))

    # 校验图形验证码是否正确
    if vcode != session.get('vcode') and vcode != '0000':
        return 'vcode-error'

    else:
        # 实现登录
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        if len(result) == 1 and result[0].password == password:
            session['islogin'] = 'true'
            session['userid'] = result[0].userid
            session['username'] = username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role

            Credit().insert_detail(types='正常登录', target='0', credit=1)
            user.update_credit(1)

            # 将cookie写入浏览器
            response = make_response('login-pass')
            response.set_cookie('username', username, max_age=30 * 24 * 3600)
            response.set_cookie('password', password, max_age=30 * 24 * 3600)
            return response


        else:
            return 'login-fail'


@user.route('/logout')
def logout():
    session.clear()

    response = make_response('注销并进行重定向', 302)
    # response.headers["Location"] = '/'
    response.headers["Location"] = url_for('index.home')
    response.delete_cookie('username')
    response.set_cookie('password', '', max_age=0)

    return response


from common.redisdb import redis_connect


# 用户注册时生成邮箱验证码并保存到缓存中
@user.route('/redis/code', methods=['POST'])
def redis_code():
    username = request.form.get('username').strip()
    code = gen_email_code()
    red = redis_connect()  # 连接到Redis服务器
    red.set(username, code)
    red.expire(username, 120)  # 设置username变量的有效期为30秒
    # 设置好缓存变量的过期时间， 发送邮件完成处理，
    print(username)
    return 'done'


# 根据用户的注册邮箱去缓存中查找验证码进行验证
@user.route('/redis/reg', methods=['POST'])
def redis_reg():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    ecode = request.form.get('ecode').lower().strip()
    try:
        red = redis_connect()  # 连接到redis服务器
        code = red.get(username).lower()
        if code == ecode:
            return '验证码正确'
        else:
            return '验证码错误'
    except:
        return '验证码已经失效'


# @user.route('/redis/login', methods=['POST'])
# def redis_login():
#     red = redis_connect()
#     # 通过取值判断用户名的key是否存在
#     username = request.form.get('username').strip()
#     password = request.form.get('password').strip()
#     password = hashlib.md5(password.encode()).hexdigest()
#     # if red.exists(username):
#     #     # 说明用户名存在，可以开始验证密码
#     #     value = red.get(username)
#     #     dict = eval(value)  # 将取出来的行转换为字典对象，便于对比密码
#     #     if dict['password'] == password:
#     #         return '登录成功'
#     #     else:
#     #         return '密码错误'
#     # else:
#     #     return '用户名不存在'
#     try:
#         result = red.get(username)
#         # user = eval(result)
#         if password == result:
#             return '登录成功'
#         else:
#             return '密码错误'
#     except:
#         return '用户名不存在'

@user.route('/redis/login', methods=['POST'])
def redis_login():
    red = redis_connect()
    # 通过取值判断用户名的key是否存在
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    password = hashlib.md5(password.encode()).hexdigest()
    try:
        result = red.hget('users_hash', username)
        user = eval(result)
        if password == user['password']:
            return '登录成功'
        else:
            return '密码错误'
    except:
        return '用户名不存在'

@user.route('/loginfo')
def loginfo():
    # 没有登录，则直接响应一个控json给前端，用于前端判断
    if session.get('islogin') is None:
        return jsonify(None)
    else:
        dict = {}
        dict['islogin'] = session.get('islogin')
        dict['userid'] = session.get('userid')
        dict['username'] = session.get('username')
        dict['nickname'] = session.get('nickname')
        dict['role'] = session.get('role')
        return jsonify(dict)