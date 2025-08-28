from setuptools import setup, find_packages

setup(
    name="KCw_WebSurferAgent",
    version="0.1.1",
    author="Richter van Emmerik",
    author_email="vanemmerik.richter@kpmg.nl",
    description="This is an agent package to automate KCw workflows.",
    packages=find_packages(),
    install_requires=[
        "autogen-ext>=0.7.1",
        "autogen-agentchat>=0.7.1",
        "autogen-core>=0.7.1",
        "azure-core>=1.35.0",
        "azure-identity>=1.23.1",
        "python-dotenv>=1.1.1",
        "requests>=2.32.4",
        "playwright>=1.54.0",
        "azure-ai-inference>=1.0.0b9",
        "aiofiles>=24.1.0",
        "aiohttp>=3.12.15",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose a license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
