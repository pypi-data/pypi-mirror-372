from setuptools import setup, find_packages


def get_version_without_initial_v(version_file_path):
    with open(version_file_path) as f:
        return f.read().strip().split("\n")[0].split("=")[-1][1:]


setup(
    name="dj_standard_enums",
    version=get_version_without_initial_v("./core/version.txt"),
    packages=find_packages(),
    include_package_data=True,
    package_data={"hb_geo": ["data/*.csv"], "core": ["version.txt"]},
    license_files=["LICENSE"],
    license="MIT",
    description="A standard way to use enums in Django and expose them via API so that they can be used in the Front End thereby reducing the code duplication.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shivamAthb/django_enums",
    author="Shivam Sharma",
    author_email="shivam.sharma@helixbeat.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=["Django>=3.2", "json-log-formatter", "djangorestframework"],
    python_requires=">=3.7",
)
