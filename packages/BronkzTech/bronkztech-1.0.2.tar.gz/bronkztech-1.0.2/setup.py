from setuptools import setup, find_packages

setup(
    name="BronkzTech",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0"
    ],
    description="Cliente para a API da BronkzTech usando token",
    author="Dran",
    url="https://discord.gg/MJ5qfSqRy8",
    python_requires=">=3.9",
)
