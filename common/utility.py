# import datetime
import random, string
import time
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw


class ImageCode:
    def gen_test(self):
        # sample 用于从一个大的列表或者字符串中，随机取的n个字符，构建出一个子列表
        list = random.sample(string.ascii_letters + string.digits, 4)
        return ''.join(list)

    def rand_color(self):
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    # ImageCode().gen_test()

    # 画一些干扰线，其中draw为PIL的ImageDraw对象
    def draw_lines(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill='black', width=2)

    def draw_verify_code(self):
        code = self.gen_test()
        width, height = 120, 50  # 设定图片大小，可根据实际需求调整
        # 创建图片对象，并设定背景色为白色
        im = Image.new('RGB', (width, height), 'white')
        # 选择使用何种字体及字体大小
        font = ImageFont.truetype(font='arial.ttf', size=40)
        draw = ImageDraw.Draw(im)  # 新建ImageDrow对象
        # 绘制字符串
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)),
                      text=code[i], fill=self.rand_color(), font=font)
        # 绘制干扰线
        self.draw_lines(draw, 2, width, height)
        # im.show()  # 可以直接将生成的图片显示出来
        # print(code)
        return im, code

    # ImageCode().draw_verify_code()
    # 生成图片验证码并返回给控制器
    def get_code(self):
        image, code = self.draw_verify_code()
        buf = BytesIO()
        image.save(buf, 'jpeg')
        bstring = buf.getvalue()  # 获取图片二进制编码
        # print(code)
        return code, bstring


# 发送邮件验证码
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header


# 发送qq邮箱验证码， 参数为收件箱地址和随机生成的验证码
def send_email(receiver, ecode):
    sender = '醒醒记笔记 <835937922@qq.com>'  # 邮箱账号和发件者签名
    # 定义发送邮件的内容，支持HTML标签和css样式
    content = f"<br/>欢迎注册醒醒记笔记博客系统账号，您的邮箱验证码为：<span style='color:red;font-size:20px;'>{ecode}</span>," \
              f"请复制到注册窗口中完成注册，感谢您的支持。<br/> "
    # 实例化邮件对象，并指定邮件的关键信息
    message = MIMEText(content, 'html', 'utf-8')
    # 指定邮件的标题，同样使用utf-8编码
    message['Subject'] = Header('醒醒记笔记的注册验证码', 'utf-8')
    message['From'] = sender  # 指定发件人信息
    message['To'] = receiver  # 指定收件人邮箱地址

    smtpObj = SMTP_SSL('smtp.qq.com')  # 建立与qq邮箱服务器的连接
    smtpObj.login(user='835937922@qq.com', password='nerftmashvtcbcac')
    # 指定发件人，收件人和邮件内容
    smtpObj.sendmail(sender, receiver, str(message))
    smtpObj.quit()


# 生成六位随机数作为邮箱验证码
def gen_email_code():
    str = random.sample(string.ascii_letters + string.digits, 6)
    return ''.join(str)

# 单个模型类转换为标准的list 数据
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                # 如果某个字段的值是datetime类型，则将其格式转为字符串
                if isinstance(v, datetime):
                    v = v.strftime('%Y-%m-%d %H:%M:%S')
                dict[k] = v
        list.append(dict)
    return list

# sqlalchemy连接查询两张表的结果集转换为[{},{}]
def model_join_list(result):
    list = []
    for obj1, obj2 in result:
        dict = {}
        for k1, v1 in obj1.__dict__.items():
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dict:  # 如果字典中已经存在相同的key则跳过
                    dict[k1] = v1
        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dict:
                    dict[k2] = v2
        list.append(dict)
    return list

# 压缩图片，通过参数width指定压缩后的图片大小
def compress_image(source, dest, width):
    from PIL import Image
    # 如果图片宽度大于1200 则调整为1200
    im = Image.open(source)
    x, y = im.size #获取图片的宽和高
    if x > width:
        # 等比例缩放
        ys = int(y * width / x)
        xs = width
        # 调整当前图片的尺寸，同时也会压缩大小
        temp = im.resize((xs, ys), Image.ANTIALIAS)
        # 将图片保存并使用80%的质量进行压缩
        temp.save(dest, quality=80)
    # 如果尺寸小于指定宽度则不缩减尺寸，只压缩保存
    else:
        im.save(dest, quality=80)

# 解析文章内容中的图片地址
def parse_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"', content)
    url_list = []
    for url in temp_list:
        # 如果图片类型为gif，则直接跳过，不对其做任何处理
        if url.lower().endswith('.gif'):
            continue
        url_list.append(url)
    return url_list

# 远程下载指定url地址的图片， 并保存到临时目录中
def download_image(url, dest):
    import requests
    response = requests.get(url) # 获取图片的响应
    # 将图片以二进制方式保存到指定文件中
    with open(file=dest, mode='wb') as file:
        file.write(response.content)

# 解析列表中的图片url地址并生成缩略图，返回缩略图名称
def generate_thumb(url_list):
    # 根据url地址解析出其文件名和域名
    # 通常使用文章内容的第一张图来生成缩略图
    # 先遍历url_list， 查找里面是否存在本地上传图片，找到即处理，代码运行结束
    for url in url_list:
        if url.startswith('/upload'):
            filename = url.split('/')[-1]
            # 找到本地图片后进行压缩，设置缩略图宽度为400像素即可
            compress_image('./resource/upload/' + filename,
                           './resource/thumb/' + filename, 400)
            return filename

    # 如果在内容中没有找到本地图片，则需要先将网络图片下载到本地，再处理
    # 直接将第一张图片作为缩略图，并生成基于时间戳的标准文件名
    url = url_list[0]
    filename = url.split("/")[-1]
    suffix = filename.split(".")[-1]  # 取得文件后缀名
    thumbname = time.strftime('%Y%m%d_%H%M%S.' + suffix)
    download_image(url, './resource/download/' + thumbname)
    compress_image('./resource/download/' + thumbname, './resource/thumb' + thumbname, 400)

    return thumbname # 返回当前缩略图的文件名

# code = gen_email_code()
# print(code)
# send_email('1020780991@qq.com', code)
