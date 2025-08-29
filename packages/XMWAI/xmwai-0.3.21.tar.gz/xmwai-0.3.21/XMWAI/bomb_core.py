import turtle
import time
from importlib.resources import files
from pathlib import Path


# U1-09 精准打击----------------------------------
def bomb(screen, t):
    """显示炸弹爆炸动画（包含坐标检查和自动预加载）"""
    x = t.xcor()
    y = t.ycor()
    # 坐标检查：不能打击自己
    if x == 0 and y == 0:
        screen.tracer(False)
        warn = turtle.Turtle()
        warn.hideturtle()
        warn.penup()
        warn.goto(0, 0)
        warn.color("#B39F2F")
        warn.write("不能打击自己", align="center", font=("微软雅黑", 16, "bold"))
        screen.update()
        time.sleep(1.5)
        warn.clear()
        screen.update()
        screen.tracer(True)
        return

    # 第一次加载时：将所有 gif 加载为 turtle 形状
    if not hasattr(bomb, "_gif_loaded"):
        gif_dir = files("XMWAI.gif")  # 注意：XMWAI/gif/__init__.py 必须存在

        bomb._shapes = []  # 保存所有完整路径
        for i in range(86):
            gif_file = gif_dir / f"{i}.gif"
            shape_path = str(gif_file)
            screen.addshape(shape_path)
            bomb._shapes.append(shape_path)

        bomb._gif_loaded = True

    # 播放爆炸动画
    screen.tracer(False)
    b = turtle.Turtle()
    b.penup()
    b.goto(x, y + 70)

    for shape_path in bomb._shapes:
        b.shape(shape_path)
        time.sleep(0.01)
        screen.update()

    # 显示文本信息
    b.hideturtle()
    text = f" 💥 成功打击\n坐标({x}, {y})"
    b.goto(x, y - 55)
    b.write(text, align="center", font=("微软雅黑", 12))

    screen.update()
    time.sleep(1.5)
    b.clear()
    screen.update()
    screen.tracer(True)
# -------------------------------------------
