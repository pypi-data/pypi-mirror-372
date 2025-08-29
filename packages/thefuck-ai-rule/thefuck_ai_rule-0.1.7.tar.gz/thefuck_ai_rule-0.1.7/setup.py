from setuptools import setup, find_packages

setup(
    name="thefuck-ai-rule",
    version="0.1.7",  # 更新版本号
    author="huchiyv",
    author_email="14727672368@163.com",
    description="AI-powered command correction assistant for thefuck",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/huchiyv/thefuckAiRule",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "thefuck>=3.0"
    ],
    entry_points={
        "console_scripts": [
            "thefuck-ai-install=thefuck_ai_assistant.installer:main",
        ],
    },
)
