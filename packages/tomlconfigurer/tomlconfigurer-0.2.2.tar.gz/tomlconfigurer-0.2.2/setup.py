from setuptools import setup, find_packages

setup(
    name="tomlconfigurer",
    version="0.2.2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["toml>=0.10"],
    python_requires=">=3.6",
    author="xystudio",
    author_email="173288240@qq.com",
    description="A configurer with toml.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/xystudio889/tomlconfigurer",
    include_package_data=True,
    entry_points={"console_scripts": ["tomlconfigurer = configurer:main"]},
    extras_require={"dev": []},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["config", "toml", "configure", "configurer"],
)
