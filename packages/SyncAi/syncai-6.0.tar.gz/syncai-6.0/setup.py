import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    lng_description = fh.read()

setuptools.setup(
    name="SyncAi",
    version="6.0",
    author="deep",
    author_email="AsyncPy@proton.me",
    license="MIT",
    description="AI designed for cybersecurity professionals, ethical hackers, Malware, and penetration testers. It assists in vulnerability analysis, security script generation, and cybersecurity research, Backdoor implementation.",
    long_description=lng_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "syncai=SyncAi.cli:console", 
        ],
    },
    python_requires=">=3.6",
    url="https://github.com/DevZ44d/SyncAi",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
