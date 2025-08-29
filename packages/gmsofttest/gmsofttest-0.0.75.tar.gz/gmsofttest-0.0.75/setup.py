import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gmsofttest",
    version="0.0.75",
    author="gmsoft1997",
    author_email="uph4rmt@dingtalk.com",
    description="大家软件内部测试技术线支撑工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.gec123.com",
    project_urls={
        "Bug Tracker": "https://www.gpwbeta.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
