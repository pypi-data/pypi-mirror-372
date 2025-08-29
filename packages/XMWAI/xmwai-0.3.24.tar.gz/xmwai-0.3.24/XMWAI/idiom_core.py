import random
import json
from importlib.resources import files
from pathlib import Path


# U2-04 成语接龙----------------------------------
def get_json_path():
    """获取 idiom.json 的正确路径（兼容 PyPI 安装后的包内资源）"""
    return Path(files("XMWAI.file").joinpath("idiom.json"))


def idiom(word, mode=0):
    """
    查询成语信息
    :param word: 要查询的成语
    :param mode: 查询模式
                 0 - 判断是否是成语，返回 True/False
                 1 - 返回拼音
                 2 - 返回解释
                 3 - 返回出处
    :return: 查询结果或 None
    """
    with open(get_json_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
        for i in data:
            if word == i["word"]:
                if mode == 0:
                    return True
                elif mode == 1:
                    return i["pinyin"]
                elif mode == 2:
                    return i["explanation"]
                elif mode == 3:
                    return i["derivation"]
        return False if mode == 0 else None


def searchIdiom(text, num=1):
    """
    模糊查询成语
    :param text: 要查询的字
    :param num: 第几个字（1~4）
    :return: 匹配的成语 或 False
    """
    wordList = []
    with open(get_json_path(), "r", encoding="utf-8") as f:
        data = json.load(f)
        for i in data:
            try:
                if text == i["word"][num - 1]:
                    wordList.append(i["word"])
            except:
                pass
    return random.choice(wordList) if wordList else False
# -------------------------------------------------
