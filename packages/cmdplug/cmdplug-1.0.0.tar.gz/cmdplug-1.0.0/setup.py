from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cmdplug",
    version="1.0.0",
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="Create simple commands in Python with ease!",
    author="HeapX",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
    ],
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["cmdplug*"]),
    project_urls={
        "Repository": "https://github.com/Security-Development/cmdplug",
    },
)
