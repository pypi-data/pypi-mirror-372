from setuptools import setup, find_packages
import codecs
import os

# 读取README内容
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="hfb_math_sdk",
    version="0.1.0",
    author="hufeibo",
    author_email="hufeibo2021@163.com",
    description="A simple math operations Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[],  # 添加任何依赖项
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'twine>=3.0.0',
        ],
    },
    project_urls={
        'Source': 'https://github.com/hfbssg/Python-SDK-demo',
    },
)