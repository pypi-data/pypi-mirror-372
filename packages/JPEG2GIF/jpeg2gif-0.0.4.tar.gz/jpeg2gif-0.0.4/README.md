
[![PyPI](https://img.shields.io/pypi/v/JPEG2GIF.svg)](https://pypi.org/project/JPEG2GIF/)
[![Python Version](https://img.shields.io/pypi/pyversions/JPEG2GIF.svg)](https://pypi.org/project/JPEG2GIF/)
[![License](https://img.shields.io/pypi/l/JPEG2GIF.svg)](https://github.com/uag515/JPEG2GIF/blob/main/LICENSE)

将多个 JPEG/JPG 图像合并为一个动画 GIF 的轻量级 Python 工具。

> 简单、快速、无需复杂配置。

## 📦 安装

使用 pip 安装：

```bash
pip install JPEG2GIF
依赖项 Pillow 会自动安装。🚀 快速使用1. 基本用法from JPEG2GIF import convert_images_to_gif

# 指定图像路径列表
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]

# 转换为 GIF
convert_images_to_gif(image_paths, "output.gif")
2. 自定义参数convert_images_to_gif(
    image_paths,
    output_path="animated.gif",
    duration=500,      # 每帧显示时间（毫秒）
    loop=0,            # 循环次数（0 表示无限循环）
    resize=None,       # 可选：调整图像大小，如 (800, 600)
    optimize=True      # 优化 GIF 文件大小
)
3. 使用通配符批量处理import glob
from JPEG2GIF import convert_images_to_gif

# 自动匹配所有 .jpg 和 .jpeg 文件
image_paths = sorted(glob.glob("frames/*.jpg") + glob.glob("frames/*.jpeg"))
convert_images_to_gif(image_paths, "result.gif", duration=200)
🖼️ 命令行使用（CLI）安装后，可直接在终端使用：# 基本用法
jpeg2gif image1.jpg image2.jpg image3.jpg -o animation.gif

# 设置帧延迟和循环
jpeg2gif *.jpg -o output.gif --duration 300 --loop 1

# 查看帮助
jpeg2gif --help
🧩 功能特性
•✅ 支持 .jpg 和 .jpeg 格式
•✅ 可调节帧延迟（duration）
•✅ 支持无限或有限循环（loop）
•✅ 可选图像缩放（resize）
•✅ 启用 GIF 优化以减小文件大小
•✅ 支持命令行和 Python API 两种调用方式
⚙️ 开发者安装开发依赖pip install -e .
pip install -r dev-requirements.txt  # 或使用 pyproject.toml 中的 dev 依赖
运行测试pytest tests/
📄 许可证本项目基于 MIT 许可证 开源。📬 反馈与问题欢迎提交 issue 或 PR：
 👉 https://github.com/uag515/JPEG2GIF/issues作者：uag515 uag515@sina.com
---

## ✅ 说明

- **替换链接**：请将 `https://github.com/uag515/JPEG2GIF` 替换为你真实的 GitHub/GitLab 仓库地址。
- **功能假设**：此 README 假设你的包提供了 `convert_images_to_gif` 函数和 `jpeg2gif` CLI 命令。如果实际 API 不同，请根据你的代码调整示例。
- **可扩展**：你可以添加“示例 GIF 图”、“性能对比”、“常见问题”等章节。

把这个 `README.md` 放在项目根目录，发布到 PyPI 后，用户在 [pypi.org/project/JPEG2GIF](https://pypi.org/project/JPEG2GIF) 上看到的就是这个漂亮的页面。
