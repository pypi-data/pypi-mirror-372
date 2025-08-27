from setuptools import setup, find_packages

setup(
    name="proxymlosy",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["requests"],
    description="A Python library to send files via Telegram",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/my_file_sender",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
