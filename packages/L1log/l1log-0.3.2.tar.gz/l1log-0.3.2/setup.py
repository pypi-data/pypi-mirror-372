import setuptools
import os.path

setupdir = os.path.dirname(__file__)

REQUIREMENTS = ["thonny>=4.0.0", "requests", "python-ldap"]
VERSION = "0.3.2"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="L1log",
    version=VERSION,
    author="Yvan PETER, Mirabelle NEBUT, Corentin DUVIVIER, Thomas BRICHE",
    author_email="mirabelle.nebut@univ-lille.fr, yvan.peter@univ-lille.fr",
    description="A plugin for Thonny that logs and send all the user's actions to an LRS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.univ-lille.fr/mirabelle.nebut/thonny-logs",
    project_urls={
    },
    platforms=["Windows", "macOS", "Linux"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education"
        
    ],
    package_data={
        "thonnycontrib": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.configuration": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.communication": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.formats": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.processing": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.event": ["*.py"],
        "thonnycontrib.thonny_LoggingPlugin.popups": ["*.py"],
    },
    packages=[  
        "thonnycontrib",
        "thonnycontrib.thonny_LoggingPlugin",
        "thonnycontrib.thonny_LoggingPlugin.processing",
        "thonnycontrib.thonny_LoggingPlugin.formats",
        "thonnycontrib.thonny_LoggingPlugin.communication",
        "thonnycontrib.thonny_LoggingPlugin.configuration",
        "thonnycontrib.thonny_LoggingPlugin.event",
        "thonnycontrib.thonny_LoggingPlugin.popups",
        
    ],
    install_requires=REQUIREMENTS,
    python_requires=">=3.10",
)
