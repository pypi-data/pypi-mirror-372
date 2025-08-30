from setuptools import setup, find_packages

setup(
    name="keynet",
    version="0.1.0",
    description="Event-driven automation library for keyboard, mouse, system, and network events.",
    author="Rudransh Joshi",
    author_email="youremail@example.com",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "pynput",
        "comtypes",
        "pycaw",
    ],
    python_requires=">=3.9",
)
