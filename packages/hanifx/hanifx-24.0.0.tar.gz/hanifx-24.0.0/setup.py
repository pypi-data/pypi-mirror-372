from setuptools import setup, find_packages

setup(
    name="hanifx",  
    version="24.0.0",  
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="Hanifx Secure Encoding Module for text and files",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/hanifx/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
)
