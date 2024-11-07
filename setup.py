"""
项目结构
Nets
- init.py
- BaseMixin.py
- BaseVar.py
- NetScene.py
"""
from setuptools import setup, find_packages

setup(
    name="Nets",
    version="0.1.0",
    author="PythonnotJava",
    author_email="2565497078@qq.com",
    description="Nets is a visualization library for drawing network graphs, based on matplotlib.",
    long_description=open("README.md", 'r', encoding='U8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PythonnotJava/Nets",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
