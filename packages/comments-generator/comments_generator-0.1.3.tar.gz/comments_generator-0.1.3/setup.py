from setuptools import setup, find_packages

setup(
    name="comments_generator",
    version="0.1.3",
    author="Yara Gafar",
    author_email="yaragafar99@gmail.com",
    url="https://github.com/yara.gafar99/comments_generator",
    description="A package for generating random comments based on category, language, and tone.",
    packages=find_packages(),  # <-- this finds subpackages automatically
    include_package_data=True,
    package_data={"comments_generator": ["data/*.csv"]},
    install_requires=["pandas"],
    python_requires=">=3.7",
)
