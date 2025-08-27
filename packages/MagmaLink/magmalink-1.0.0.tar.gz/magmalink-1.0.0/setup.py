import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MagmaLink",
    version="1.0.0",
    author="southctrl",
    author_email="rive4785@gmail.com",
    description="A simple lavalink wrapper easy to use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/southctrl/magmalink",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)