from setuptools import setup, find_packages

setup(
    name="datatensor",
    version="0.2",
    author="Iyazkasep",
    author_email="iyaz.kasep2009@gmail.com",
    description="Lightweight library ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/DataTensor/",
    packages=find_packages(),
    py_modules=["datatensor"],  # ganti sesuai nama file python utama kamu
    install_requires=[
        "numpy>=1.24.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
