from setuptools import setup

setup(
    name="llm-rovodev",
    version="0.1.2",
    description="LLM plugin exposing the RovoDev model for the llm CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/possibly/llm-rovodev",
    project_urls={
        "Homepage": "https://github.com/possibly/llm-rovodev",
        "Repository": "https://github.com/possibly/llm-rovodev",
        "Changelog": "https://github.com/possibly/llm-rovodev/releases",
    },
    author="Tyler Brothers",
    author_email="tylerbrothers1@gmail.com",
    license="Apache-2.0",
    py_modules=["llm_rovodev"],
    python_requires=">=3.8",
    install_requires=[
        "llm>=0.14.0",
    ],
    entry_points={
        "llm": [
            "llm_rovodev = llm_rovodev",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
    ],
)
