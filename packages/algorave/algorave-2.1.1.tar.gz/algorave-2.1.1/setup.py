from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    "numpy>=1.24.4",
    "scipy>=1.10.0",
    "PyYAML",
    "typing-extensions>=4.9.0; python_version<'3.10'",
    "pydantic>=2.9.2",
    "algocore==0.1.0",
    "eval-type-backport; python_version<'3.10'",
]

# Simplified OpenCV dependency - only use opencv-python for GUI support
INSTALL_REQUIRES.append("opencv-python>=4.9.0.80")

setup(
    packages=find_packages(exclude=["tests", "tools", "benchmark"], include=['algorave*']),
    install_requires=INSTALL_REQUIRES,
)
