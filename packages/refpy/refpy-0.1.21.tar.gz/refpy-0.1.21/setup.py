from setuptools import setup, find_packages

setup(
    name="refpy",
    version="0.1.21",
    description="Package for subsea pipelines and risers design in Python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/refpy/refpy",
    author="ismael-ripoll",
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[],
    project_urls={
        "Documentation": "https://refpy.github.io/refpy",
        "Source": "https://github.com/refpy/refpy",
        "Tracker": "https://github.com/refpy/refpy/issues",
    }
)