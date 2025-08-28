from setuptools import setup, find_packages

setup(
    name="asr_business",
    version="v0.4.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    describe="ASR Python package for identifying business audio data",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    python_requires=">=3.8",
    license="MIT Licence",
    url="https://github.com/Tonywu2018/asr_business",
    author="wuwenxiao",
    author_email="wuwenxiao@inke.cn",
    include_package_data=True,
    platforms="any",
    install_requires=[
            "torch==2.4.0",
            "funasr",
            "funasr-onnx",
            "noisereduce",
            "pydub",
            "soundfile"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
