from setuptools import setup, find_packages

setup(
    name="ShamsiCalendar",  # نام پکیج در PyPI
    version="0.1.1",
    author="Poriya Delavariyan",
    author_email="poria.dell7@gmail.com",
    description="Persian (Shamsi) Calendar and Date Entry for Python Tkinter",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/p7deli/ShamsiCalendar",
    packages=find_packages(),
    install_requires=[
        "customtkinter",
        "jdatetime"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
