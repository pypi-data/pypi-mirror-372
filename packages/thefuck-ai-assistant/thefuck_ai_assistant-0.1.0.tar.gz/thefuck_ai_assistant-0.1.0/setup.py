from setuptools import setup, find_packages

setup(
    name="thefuck-ai-assistant",
    version="0.1.0",
    author="huchiyv",
    author_email="your.email@example.com",  # 请替换为您的实际邮箱
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
