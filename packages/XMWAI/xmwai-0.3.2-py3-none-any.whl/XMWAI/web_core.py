import os
import json
import requests
from flask import Flask, render_template
import re
from pyecharts import options as opts
from pyecharts.charts import Pie
import webbrowser
import threading
import time
from importlib.resources import files
from pathlib import Path


'''Super堡'''
# 搭建flask框架
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

mapping = {
    "面包底": "BottomBun",
    "生菜": "lettuce",
    "番茄": "tomato",
    "牛肉饼": "beef",
    "芝士": "cheese",
    "酱料": "sauce",
    "面包顶": "TopBun"
}

ingredients_order = []


def burger(result):
    global ingredients_order
    inputs = result.strip().split("→")
    ingredients_order = [mapping[i] for i in inputs]
    ingredients_order = ingredients_order[::-1]

    # 自动启动服务器
    start_server()
    return ingredients_order


@app.route('/')
def show_burger():
    return render_template("burger.html", ingredients=ingredients_order)


def run_server(port=5050):
    """在后台线程中运行服务器"""
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)


def start_server(port=5050):
    """启动服务器并打开浏览器"""
    url = f"http://127.0.0.1:{port}/"

    # 在后台线程中启动服务器
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    # 等待服务器启动
    time.sleep(2)

    # 打开浏览器
    webbrowser.open(url)

    # 保持服务器运行
    try:
        server_thread.join()
    except KeyboardInterrupt:
        pass


'''Random料理屋'''
# 食材对应 emoji
emoji_dict = {
    "鸡": "🍗", "牛": "🥩", "猪": "🥓", "鱼": "🐟", "虾": "🦐", "蟹": "🦀",
    "豆腐": "🧈", "土豆": "🥔", "胡萝卜": "🥕", "西红柿": "🍅", "青菜": "🥬",
    "菠菜": "🥬", "蘑菇": "🍄", "玉米": "🌽", "米饭": "🍚", "面条": "🍜",
    "面包": "🍞", "奶酪": "🧀", "鸡蛋": "🥚", "牛奶": "🥛", "橙子": "🍊",
    "苹果": "🍎", "香蕉": "🍌"
}

# 动作对应 emoji
action_dict = {
    "炒": "🍳", "煮": "🍲", "烤": "🔥", "蒸": "♨️", "炸": "🍟", "拌": "🥣",
    "切": "🔪", "腌": "🫙", "炖": "🥘"
}


def add_emoji_to_text(text):
    for key, val in action_dict.items():
        text = re.sub(f'({key})', f'{val} \\1', text)
    for key, val in emoji_dict.items():
        text = re.sub(f'({key})', f'{val} \\1', text)
    return text


def format_section_steps(text):
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    lines = lines[:50]
    return "<br>".join(add_emoji_to_text(line) for line in lines)


def parse_nutrition_section(text):
    """解析 API 返回的营养 JSON 并提取数值"""
    default_data = {"蛋白质": 30, "脂肪": 20, "碳水化合物": 50, "维生素": 10, "矿物质": 5}

    def extract_number(val):
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            match = re.search(r"(\d+(\.\d+)?)", val)
            if match:
                return float(match.group(1))
        return 0

    try:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            parsed = json.loads(match.group())
            result = {}
            for key in default_data.keys():
                if key in parsed:
                    val = parsed[key]
                    if isinstance(val, dict):
                        total = sum(extract_number(v) for v in val.values())
                        result[key] = total
                    else:
                        result[key] = extract_number(val)
                else:
                    result[key] = default_data[key]
            return result
    except Exception as e:
        print("JSON解析失败:", e)
    return default_data


def generate_pie_chart(data_dict, filename: Path):
    data = [(k, v) for k, v in data_dict.items()]
    pie = (
        Pie(init_opts=opts.InitOpts(width="1100px", height="500px"))
        .add("", data)
        .set_global_opts(title_opts=opts.TitleOpts(title="营养价值分布"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    pie.render(str(filename))
    return filename


def cookbook(m, t, s, key):
    if key != "CaJQ":
        return "密钥错误，无法生成食谱。"

    # 调用 API 生成创意菜谱
    messagesList = [
        {"role": "system", "content": "天马行空的创意菜厨师"},
        {"role": "user", "content": f"请以{m}为主菜，{s}为配菜，{t}为烹饪方式写一个创意食谱，"
                                    "结果中不要*，并且结果只需要创意灵感、食材清单、制作步骤、"
                                    "食材搭配的营养价值四种大标题内容。食材搭配的营养价值部分请输出标准 JSON，"
                                    "键为蛋白质、脂肪、碳水化合物、维生素、矿物质，值为数值及说明。"}
    ]

    url = "https://qianfan.baidubce.com/v2/chat/completions"
    payload = json.dumps({"model": "ernie-4.5-turbo-32k",
                         "messages": messagesList}, ensure_ascii=False)
    headers = {
        "Content-Type": "application/json",
        "appid": "",
        "Authorization": "Bearer bce-v3/ALTAK-cGbxpVA5AbSz6h8nbLaFh/b539762075d55c76d93dc78bcf0a91beeaf0490a"
    }

    try:
        response = requests.post(url, headers=headers,
                                 data=payload.encode("utf-8"))
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"接口调用失败：{e}"

    # 分割内容
    sections = re.split(r"(创意灵感|食材清单|制作步骤|食材搭配的营养价值)", content)
    body_sections = [""]*4
    title_map = {"创意灵感": 0, "食材清单": 1, "制作步骤": 2, "食材搭配的营养价值": 3}
    i = 1
    while i < len(sections):
        header = sections[i]
        text_sec = sections[i+1] if i+1 < len(sections) else ""
        idx = title_map.get(header.strip(), None)
        if idx is not None:
            body_sections[idx] = text_sec.strip()
        i += 2

    # 获取包内模板和图片目录
    templates_dir = Path(files("XMWAI").joinpath("templates"))
    templates_dir.mkdir(exist_ok=True)
    photo_dir = Path(files("XMWAI").joinpath("xmw_photo"))

    # 生成饼图文件
    pie_chart_file = templates_dir / "nutrition_pie.html"
    nutrient_data = parse_nutrition_section(body_sections[3])
    generate_pie_chart(nutrient_data, pie_chart_file)

    # 添加 emoji
    m_emoji = add_emoji_to_text(m)
    s_emoji = add_emoji_to_text(s)
    t_emoji = add_emoji_to_text(t)

    # 步骤顺序 HTML
    step_titles = ["食材搭配的营养价值", "创意灵感", "食材清单", "制作步骤"]
    steps_order = [3, 0, 1, 2]
    steps_html = ""
    for i, idx in enumerate(steps_order):
        if idx == 3:
            section_content_html = "根据食材搭配生成的营养价值饼图如下 ⬇️"
        else:
            section_content_html = format_section_steps(body_sections[idx])
        steps_html += f"""
        <div class="step-card" style="animation-delay:{(i+1)*0.2}s;">
            <div class="step-title">Step {i+1} 📝 {step_titles[i]}</div>
            <div class="step-content">{section_content_html}</div>
        </div>
        """

    # HTML 页面
    bg_path = photo_dir / "bg.jpeg"
    html = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>创意菜谱</title>
        <style>
            html, body {{ margin:0; padding:0; width:100%; height:100%; overflow-x:hidden; }}
            body {{ font-family:"微软雅黑",sans-serif; background:#2c2c2c url('{bg_path.resolve()}') no-repeat center center fixed; background-size:cover; color:#333; }}
            .container {{ max-width:1200px; margin:30px auto; background:rgba(255,248,220,0.95); border-radius:15px; padding:30px; box-shadow:0 0 20px rgba(0,0,0,0.2); }}
            .banner {{ width:100%; height:220px; background:url('{bg_path.resolve()}') center/cover no-repeat; border-radius:15px 15px 0 0; display:flex; align-items:center; justify-content:center; }}
            .banner h1 {{ color:#fff; font-size:28px; text-shadow:1px 1px 3px #666; }}
            p {{ font-size:18px; margin:8px 0; }}
            .step-card {{ background:#fff0b3; margin:10px 0; border-radius:12px; overflow:hidden; opacity:0; transform:translateY(20px) scale(0.98); animation:fadeInUp 0.6s forwards; }}
            .step-title {{ font-weight:bold; padding:10px 15px; cursor:pointer; background:#ffb347; color:#fff; border-bottom:1px solid #ffd27f; }}
            .step-content {{ padding:10px 15px; display:block; font-size:16px; opacity:0; max-height:0; overflow:hidden; transition: opacity 0.4s ease, max-height 0.4s ease; }}
            .step-card.hover .step-content {{ opacity:1; max-height:800px; }}
            iframe {{ width:100%; height:500px; border:none; margin-top:20px; }}
            @keyframes fadeInUp {{ to {{ opacity:1; transform:translateY(0) scale(1); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="banner"><h1>🍽 {m+t+s}</h1></div>
            <p>🍖 <strong>主菜：</strong>{m_emoji}</p>
            <p>🥗 <strong>配菜：</strong>{s_emoji}</p>
            <p>👩‍🍳 <strong>做法：</strong>{t_emoji}</p>
            {steps_html}
            <iframe src="{pie_chart_file.resolve()}"></iframe>
        </div>
        <script>
            const steps = document.querySelectorAll('.step-card');
            steps.forEach(card => {{
                card.addEventListener('mouseenter', () => {{ card.classList.add('hover'); }});
                card.addEventListener('mouseleave', () => {{ card.classList.remove('hover'); }});
            }});
        </script>
    </body>
    </html>
    """

    # 保存 HTML 文件到包内 templates
    safe_title = re.sub(r'[\/\\:*?"<>|]', "", m+t+s)
    html_file = templates_dir / f"{safe_title}_菜谱.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    # 打开浏览器
    webbrowser.open(f"file://{html_file.resolve()}")

    return content
