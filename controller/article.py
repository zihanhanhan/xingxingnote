import math
import os

from flask import Blueprint, abort, render_template, request, session

from common.utility import parse_image_url, generate_thumb
from module.article import Article
from module.comment import Comment
from module.credit import Credit
from module.favorite import Favorite
from module.users import Users

article = Blueprint('article', __name__)


@article.route('/article/<int:articleid>')
def read(articleid):
    try:
        # 数据格式： （Article，‘nickname’）
        result = Article().find_by_id(articleid)
        if result is None:
            abort(404)
    except:
        abort(500)

    dict = {}
    for k, v in result[0].__dict__.items():
        if not k.startswith('_sa_instance_state'):
            dict[k] = v
    dict['nickname'] = result.nickname
    # print(dict)

    # credit1 = Article().how_many_credit(articleid)
    # print(credit)
    if dict['credit'] == 0 or dict['nickname'] == session.get('nickname'):
        # print(dict['credit'])
        payed = True
        content = dict['content']
        temp = content[0:int(len(content))]
        position = temp.rindex('</p>') + 4
        dict['content'] = temp[0:position]

    else:
        # 如果已经消耗积分，则不再截取文章内容
        payed = Credit().check_payed_article(articleid)

        position = 0

        if not payed:
            content = dict['content']
            temp = content[0:int(len(content) / 2)]
            if "</p>" in temp:
                position = temp.rindex('</p>') + 4
                dict['content'] = temp[0:position]
            else:
                position = int(len(content) / 2)
                dict['content'] = temp[0:position] + '</p>'

    is_favorite = Favorite().check_favorite(articleid)

    Article().update_read_count(articleid)  # 阅读次数+1

    # 获取当前文章的上一篇和下一篇
    prev_next = Article().find_prev_next_by_id(articleid)

    # 显示当前文章对应的评论
    # comment_user = Comment().find_limit_with_user(articleid, 0, 50)

    comment_list = Comment().get_comment_user_list(articleid, 0, 10)

    count = Comment().get_count_by_article(articleid)
    total = math.ceil(count / 10)

    return render_template('article-base.html', article=dict, position=position, payed=payed,
                           is_favorite=is_favorite, prev_next=prev_next,
                           total=total)


@article.route('/readall', methods=['POST'])
def read_all():
    position = int(request.form.get('position'))
    articleid = request.form.get('articleid')
    article = Article()
    result = article.find_by_id(articleid)
    content = result[0].content[position:]

    # 如果已经消耗积分，则不再扣除
    payed = Credit().check_payed_article(articleid)
    if not payed:
        # 添加积分明细
        Credit().insert_detail(types='阅读文章', target=articleid, credit=-1 * result[0].credit)
        # 减少用户表的剩余积分
        Users().update_credit(credit=-1 * result[0].credit)

    return content


@article.route('/ucenter/post')
def pre_post():
    return render_template('post-2.html')


@article.route('/article', methods=['POST'])
def add_article():
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    credit = int(request.form.get('credit'))
    drafted = int(request.form.get('drafted'))
    checked = int(request.form.get('checked'))
    articleid = int(request.form.get('articleid'))

    if session.get('userid') is None:
        return 'perm-denied'
    else:
        user = Users().find_by_userid(session.get('userid'))
        if user.role == 'editor':
            # 权限合格， 可以执行发布文章的代码
            # 首先为文章生成缩略图，优先从内容中找，找不到则随即生成一张
            url_list = parse_image_url(content)
            if len(url_list) > 0:  # 表示文章中存在图片
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，则根据文章类别指定一张缩略图
                thumbname = '%d.png' % type
            # try:
            #     id = Article().insert_article(type=type, headline=headline, content=content, credit=credit,
            #                                   thumbnail=thumbname, drafted=drafted, checked=checked)

            # 判断articleid是否为0， 如果为0则表示是新数据
            if articleid == 0:
                try:
                    id = Article().insert_article(type=type, headline=headline, content=content,
                                                  credit=credit, thumbnail=thumbname,
                                                  drafted=drafted, checked=checked)

                    # 新增文章成功后，将已经静态化的文章列表页面全部删除，便于生成新的静态文件
                    list = os.listdir('./template/index-static/')
                    for file in list:
                        os.remove('./template/index-static/' + file)
                    return str(id)
                except Exception as e:
                    return 'post-fail'
            else:
                # 如果是已经添加过的文章，则修改操作
                try:
                    id = Article().update_article(articleid=articleid, type=type, headline=headline,
                                                  content=content, credit=credit, thumbnail=thumbname,
                                                  drafted=drafted, checked=checked)
                    return str(id)
                except Exception as e:
                    return 'post-fail'

        # 如果角色不是作者，则只能投稿，不能正式发布
        elif checked == 1:
            return 'perm-denied'
        else:
            return 'perm-denied'


@article.route('/article/<int:articleid>', methods=['DELETE'])
def cancel_article(articleid):
    try:
        article().cancel_article(articleid)
        return 'cancel-pass'
    except:
        return 'cancel-fail'