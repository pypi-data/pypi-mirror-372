from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-modeladmin-reorder-reborn-again",
    version="0.1.0",
    description="Custom ordering for the apps and models in the admin app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amphr/django-modeladmin-reorder-reborn-again",
    author="amphr",
    author_email="",
    license="BSD-3-Clause",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    include_package_data=True,
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "Django >= 4.1",
    ],
)
