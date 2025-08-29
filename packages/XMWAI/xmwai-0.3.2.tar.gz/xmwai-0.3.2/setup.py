from setuptools import setup, find_packages

setup(
    name="XMWAI",  # 包名（pip install XMWAI）
    version="0.3.2",  # 每次上传记得升级版本号
    author="pydevelopment",  # 作者
    author_email="hekai@xiaoma.cn",  # 邮箱
    description="Small code King AI related library",  # 简短描述
    long_description=open("README.md", encoding="utf-8").read(),  # 详细描述
    long_description_content_type="text/markdown",  # 描述格式
    url="https://github.com/Tonykai88/XMWAI.git",  # GitHub 链接
    packages=find_packages(),  # 自动找包
    include_package_data=True,  # 打包额外资源的开关
    package_data={  # 👇 显式告诉 setuptools 要包含哪些非 py 文件
        "XMWAI.file": ["idiom.json"],
        "XMWAI": [
            "templates/*.html",
            "static/*.js",
            "static/*.css",
            "static/images/*"
        ],
        "XMWAI.gif": ["*.gif"],  # gif 文件夹下的所有 GIF
        "XMWAI.file": ["*.json"]  # file 文件夹下的 json
    },
    install_requires=[
        "requests>=2.32.3",   # 依赖包
        "Pillow>=11.1.0",     # 图像处理库
        "opencv-python>=3.4.18.65",  # OpenCV 库
        "numpy>=1.26.0",      # 数值计算库
        "flask>=3.1.0",        # Web 框架
        "pyecharts>=2.0.8"    # 图表绘制库
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.0',  # 支持的 Python 版本
)
