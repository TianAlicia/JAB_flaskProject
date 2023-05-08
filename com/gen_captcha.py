from io import BytesIO
from random import choices

from captcha.image import ImageCaptcha
from PIL import Image


def gen_captcha(content="012345689"):
    """生成验证码"""
    image = ImageCaptcha()
    # 获取字符串
    captcha_text = "".join(choices(content, k=4))  # 从 content 里面随机选取四个内容
    # 生成图像
    # print(image.generate(captcha_text))
    data = image.generate(captcha_text)
    captcha_image = Image.open(data)

    out = BytesIO()
    captcha_image.save(out, "png")

    # resp = make_response(out.read())
    # resp.content_type = 'image/png'
    return captcha_text, captcha_image


# 生成验证码
def get_captcha_image():
    code, image = gen_captcha()
    out = BytesIO()
    # session["code"] = code
    image.save(out, "png")
    out.seek(0)
    content = out.read()  # 读取图片的二进制数据做成响应体
    return content, code


if __name__ == "__main__":
    text, img = get_captcha_image()
    print(text)
    print(img)
