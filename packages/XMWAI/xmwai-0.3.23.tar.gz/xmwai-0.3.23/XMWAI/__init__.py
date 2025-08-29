from .core import story, photo, reply, poem, crack  # 从子模块导入函数到顶层
from .magic_core import birthday  # 从子模块导入函数到顶层
from .bomb_core import bomb  # 从子模块导入函数到顶层
from .idiom_core import idiom, searchIdiom, get_json_path  # 从子模块导入函数到顶层
from .trial_class import make, get_file_content_as_base64, save_pic, detect_windows_scale, get_file_content_as_base64_2, cartoon  # 从子模块导入函数到顶层
from .web_core import burger, cookbook  # 从子模块导入函数到顶层

__all__ = ["story", "photo", "reply", "poem", 'birthday', 'bomb',
           "idiom", "searchIdiom", "get_json_path", "crack",
           "make", "get_file_content_as_base64", "save_pic", "detect_windows_scale",
           "get_file_content_as_base64_2", "cartoon", "burger", "cookbook"]  # 可选：明确导出的内容
