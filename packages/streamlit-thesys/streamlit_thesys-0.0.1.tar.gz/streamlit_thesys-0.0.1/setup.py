from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-thesys",
    version="0.0.1",
    author="Thesys",
    author_email="engineering@thesys.dev",
    description="Generative UI for Streamlit powered by C1 by Thesys",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thesysdev/streamlit-thesys-genui",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
        "requests >= 2.31.0",
        "pandas >= 1.3.0",
        "openpyxl >= 3.0.0",  # For Excel file support
    ],
    keywords=[
        "Streamlit",
        "Thesys",
        "C1 by Thesys",
        "Generative UI",
        "LLM UI",
        "AI components",
        "live data visualization",
        "data visualization",
        "agent UI",
        "LLM to UI",
        "streamlit components",
        "generative visualization",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
            "openai", # Required for the example.py file
        ]
    }
)
