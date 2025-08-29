from setuptools import setup, find_packages

setup(
    name="fullscreen-alert",
    version="0.1.2",
    author="pengmin",
    author_email="877419534@qq.com",
    description="A simple fullscreen alert window module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    keywords="tkinter, fullscreen, alert, gui",
)