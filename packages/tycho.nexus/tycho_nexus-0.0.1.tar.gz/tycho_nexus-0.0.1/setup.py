import setuptools


setuptools.setup(
    # info
    name="tycho.nexus",
    description="The official Python API wrapper for Nexus, by Tycho",
    license="MIT",
    # README
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # SCM versioning (git tags)
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    # author
    author="Tycho",
    author_email="mail@tycho.team",
    # find and add packages
    packages=setuptools.find_packages(),
    include_package_data=True,
    # requirements and search
    python_requires=">=3.8",
    install_requires=["httpx", "asyncio", "websockets"],
    classifiers=["Framework :: AsyncIO"],
    keywords=["nexus", "tycho"],
)
