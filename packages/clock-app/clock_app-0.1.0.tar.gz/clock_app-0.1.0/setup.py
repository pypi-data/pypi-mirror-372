# clock_app/setup.py
from setuptools import setup, find_packages

setup(
    name="clock-app",              # PyPI 上名字用连字符
    version="0.1.0",
    packages=find_packages(),      # 只打包 clock_app 包
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "clock = clock_app.my_clock:main",
        ],
    },
    author="Your Name",
    description="A simple CLI clock",
    url="https://github.com/Kevin589981/clock-app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)