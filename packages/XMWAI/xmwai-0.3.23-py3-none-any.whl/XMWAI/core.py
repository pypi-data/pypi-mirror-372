import re
import requests
import json
import os
import zipfile


# U1-02 Story GPT----------------------------------
def story(role, time, address, event, key=""):
    content = role+time+address+event
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    data = {
        "max_tokens": 1000,     # 回复长度限制
        "top_k": 4,             # 灵活度
        "temperature": 0.5,     # 随机性
        "messages": [
            {
                # 设置对话背景或赋予模型角色，该设定会贯穿整轮对话，对全局的模型生成结果产生影响。对应作为'role'为'system'时，'content'的值
                "role": "system",
                "content": "我是一个非常会写童话的儿童写作作家,根据我写出的关键词，帮我生成一篇童话故事。"
            },
            {
                # 对大模型发出的具体指令，用于描述需要大模型完成的目标任务和需求说明。会与角色设定中的内容拼接，共同作为'role'为'system'时，'content'的值
                "role": "user",
                "content": content
            }
        ],
        "model": "4.0Ultra"
    }
    data["stream"] = True
    if key == "":
        print("没有秘钥！请提供秘钥！")
        return "没有秘钥！请提供秘钥！"
    elif key != "CaJQ":
        print("秘钥错误！请重新输入！")
        return "秘钥错误！请重新输入！"
    header = {
        "Authorization": "Bearer paNyL"+key+"OpyOBmflKZp:yhBhAlSFMwaqlVKAtDbv"
    }
    response = requests.post(url, headers=header, json=data, stream=True)

    # 流式响应解析示例
    response.encoding = "utf-8"
    contents = ""
    result = response.iter_lines(decode_unicode="utf-8")
    result = str(list(result))

    # 正则表达式模式
    pattern = r'"content":"(.*?)"'

    # 使用re.findall查找所有匹配的内容
    contents = re.findall(pattern, result, re.DOTALL)
    s = ""
    for i in contents:
        s += i
    s = s.replace('\\', "")
    s = s.replace("n", "")
    return s
# -------------------------------------------------


# U1-06 我说你画-----------------------------------
def photo(content, style, size, key=""):
    # 图像生成的 API URL
    if key == "":
        print("没有秘钥！请提供秘钥！")
        return "没有秘钥！请提供秘钥！"
    elif key != "CaJQ":
        print("秘钥错误！请重新输入！")
        return "秘钥错误！请重新输入！"
    key = "image"
    url = "https://gateway.xiaomawang.com/pythonUILibApi/api/text2" + key

    # 请求的头部
    headers = {
        "Content-Type": "application/json"
    }
    resolution = {"1024*1024": 3, "1280*720": 4, "720*1280": 5}
    if content == "":
        return
    if style == "":
        style = "默认"
    if size == "":
        size = "1024*1024"

    # 请求的主体内容
    data = {
        'prompt': content,  # 你想要生成的图像描述
        'imgStyle': style,
        'imgSize': resolution[size]  # 图像的尺寸
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=data)

    # 检查请求是否成功
    if response.status_code == 200:
        response_data = response.json()
        _data = eval(str(response_data))
        photo_url = _data["data"][0]["url"]

    skin = requests.get(photo_url).content
    with open("{}.png".format(content), 'wb') as s:
        s.write(skin)
# ------------------------------------------------


# U1-11 百变助手----------------------------------
def reply(role, content, key=""):
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    data = {
        "max_tokens": 60,     # 回复长度限制
        "top_k": 5,             # 灵活度
        "temperature": 0.6,     # 随机性
        "messages": [
            {
                # 设置对话背景或赋予模型角色，该设定会贯穿整轮对话，对全局的模型生成结果产生影响。对应作为'role'为'system'时，'content'的值
                "role": "system",
                "content": "你是一位非常优秀的" + role + "，请根据我的提问，非常科学、有趣和严谨的回答我。"
            },
            {
                # 对大模型发出的具体指令，用于描述需要大模型完成的目标任务和需求说明。会与角色设定中的内容拼接，共同作为'role'为'system'时，'content'的值
                "role": "user",
                "content": content + "(一定要80个字左右，语句必须完整，语句必须完整，不准出现断句。)"
            }
        ],
        "model": "4.0Ultra"
    }
    data["stream"] = True
    if key == "":
        print("没有秘钥！请提供秘钥！")
        return "没有秘钥！请提供秘钥！"
    elif key != "CaJQ":
        print("秘钥错误！请重新输入！")
        return "秘钥错误！请重新输入！"
    header = {
        "Authorization": "Bearer paNyL"+key+"OpyOBmflKZp:yhBhAlSFMwaqlVKAtDbv"
    }
    response = requests.post(url, headers=header, json=data, stream=True)

    # 流式响应解析示例
    response.encoding = "utf-8"
    contents = ""
    result = response.iter_lines(decode_unicode="utf-8")
    result = str(list(result))

    # 正则表达式模式
    pattern = r'"content":"(.*?)"'

    # 使用re.findall查找所有匹配的内容
    contents = re.findall(pattern, result, re.DOTALL)
    s = "   "
    for i in contents:
        s += i
    if '\\' in s:
        s = s.replace('\\', "")
    if '*' in s:
        s = s.replace('*', "")
    sum_ = """"""
    for i in range(0, len(s), 17):
        sum_ = sum_ + s[i:i+17] + "\n"
    return sum_
# ------------------------------------------------


# U2-05 码字成诗----------------------------------
def poem(title, key=""):
    if key == "":
        print("没有秘钥！请提供秘钥！")
        return "没有秘钥！请提供秘钥！"
    elif key != "CaJQ":
        print("秘钥错误！请重新输入！")
        return "秘钥错误！请重新输入！"
    messagesList = [
        {
            "role": "system",
            "content": "唐代诗人"
        },
        {
            "role": "user",
            "content": f"请以《{title}》为题，创作一首七言绝句，每句7个字，一共4句，符合古诗韵律规范，内容积极乐观向上，适合中小学生阅读，不要解析，不要题目，不要标点符号，所有文字放在一行"
        }
    ]

    url = "https://qianfan.baidubce.com/v2/chat/completions"

    payload = json.dumps({
        "model": "ernie-4.5-turbo-32k",
        "messages": messagesList
    }, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'appid': '',
        'Authorization': 'Bearer bce-v3/ALTAK-cGbxpVA5AbSz6h8nbLaFh/b539762075d55c76d93dc78bcf0a91beeaf0490a'
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload.encode("utf-8"))

    response_data = json.loads(response.text)
    content = response_data["choices"][0]["message"]["content"]
    content = content.replace("\n", "")
    while " " in content:
        content = content.replace(" ", "")
    return content
# ------------------------------------------------


# U2-06 凯撒加密----------------------------------
def crack(name, pwd):
    try:
        zFile = zipfile.ZipFile(name + ".zip")
        zFile.extractall(pwd=str(pwd).encode())
        print("已成功破解密码")
        os.system("Treasuremap.png")
    except:
        print("密码错误")
# ------------------------------------------------
