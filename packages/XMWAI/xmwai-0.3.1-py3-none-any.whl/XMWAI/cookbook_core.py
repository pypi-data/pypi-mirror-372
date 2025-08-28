import requests
import json
import webbrowser
import re


def cookbook(m, t, s, key):
    if key != "CaJQ":
        return "密钥错误，无法生成食谱。"

    messagesList = [
        {
            "role": "system",
            "content": "天马行空的创意菜厨师"
        },
        {
            "role": "user",
            "content": f"请以{m}为主菜，{s}为配菜，{t}为烹饪方式写一个创意食谱，结果中不要*"
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

    try:
        response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
        response_data = json.loads(response.text)
        content = response_data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"接口调用失败：{e}"

    # 提取标题和正文（防止 IndexError）
    lines = content.strip().split("\n")
    title = lines[0] if len(lines) >= 1 else "创意菜谱"
    content_body = "\n".join(lines[1:]) if len(lines) >= 2 else "（无正文内容）"

    # 构造 HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
    margin: 0;
    padding: 0;
    font-family: "微软雅黑", sans-serif;
    background: #2c2c2c url('bg.jpeg') no-repeat center center fixed;
    background-size: cover;
    color: #eee;
}}

.container {{
    max-width: 800px;
    margin: 40px auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 40px 40px 30px 40px;
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.3);
    color: #333;
}}

.banner {{
    position: relative;
    width: 100%;
    height: 250px;
    background-image: url('bg.jpeg');
    background-size: cover;
    background-position: center;
    border-radius: 15px 15px 0 0;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.banner::after {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 15px 15px 0 0;
}}

.banner h1 {{
    position: relative;
    color: #fff;
    font-size: 28px;
    text-shadow: 1px 1px 4px #000;
    z-index: 1;
}}

h2 {{
    color: #555;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
    margin-top: 20px;
}}

p {{
    font-size: 18px;
    margin: 10px 0;
}}

pre {{
    background: #f8f8f8;
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
    font-family: "Courier New", monospace;
    font-size: 16px;
}}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="banner">
                <h1>🍽 {title}</h1>
            </div>
            <p><strong>主菜：</strong>{m}</p>
            <p><strong>配菜：</strong>{s}</p>
            <p><strong>做法：</strong>{t}</p>
            <h2>生成的食谱：</h2>
            <pre>{content_body}</pre>
        </div>
    </body>
    </html>
    """

    # 保存为 HTML 文件
    filename = title.strip().replace(" ", "_").replace("：", "").replace(":", "") + ".html"
    filename = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', f"{title}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # 自动打开网页
    webbrowser.open(filename)

    return content + "\n"
