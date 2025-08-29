from setuptools import setup, find_packages

setup(
    name="webnetwork",
    version="1.2.3",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "scapy>=2.5.0"
    ],
    python_requires=">=3.8",
    description="Automatic web server monitoring and defensive DoS/DDoS detection with blocking",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="hackinglab",
    author_email="mrfidal@proton.me",
    url="https://github.com/bytebreach/webnetwork",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    entry_points={
        "console_scripts": [
            "webnetwork=webnetwork.detector:start"
        ],
    },
)
