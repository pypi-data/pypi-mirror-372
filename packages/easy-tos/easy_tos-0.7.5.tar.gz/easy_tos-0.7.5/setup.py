from setuptools import setup, find_packages


setup(
    name="easy_tos",  # 库的名称
    version="0.7.5",      # 版本号
    author="Jiaqi Wu",
    description="A simple wrapper for tos",  # 描述
    long_description=open("README.md", "r", encoding="utf-8").read(),  # 长描述，从README.md读取<e
    long_description_content_type="text/markdown",  # 长描述的格式，这里是markdown<e
    packages=find_packages(),  # 自动找到所有包
    install_requires=[  
        'tos',
        "tqdm",
        "pillow",
        "pandas"
    ],
    classifiers=[  # 可选，帮助别人找到你的库
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
)