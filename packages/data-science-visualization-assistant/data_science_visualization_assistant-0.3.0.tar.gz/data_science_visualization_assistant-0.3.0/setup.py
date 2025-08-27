from setuptools import setup, find_packages
from pathlib import Path


def read_requirements():
    with open(r"C:\Users\VISHNU\Desktop\datascienceassiest\data-science-visualization-assistant\requirements.txt") as f:
        return f.read().splitlines()


description = """
A Streamlit application that acts as your personal data visualization expert, 
powered by LLMs. Simply upload your dataset and ask questions in natural language - the AI agent will analyze your data, 
generate appropriate visualizations, and provide insights through a combination of charts, statistics, and explanations.
"""

setup(
    name="data-science-visualization-assistant",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "e2b-code-interpreter==1.0.3",
        "pandas",
        "numpy",
        "matplotlib",
        "streamlit",
        "e2b",
        "Pillow",
        "python-dotenv",
        "groq"
    ],
    author="Vishnu",
    author_email="vishnurrajeev@gmail.com",
    description=description,  # Keep this short
    long_description=Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/Vishnuu011/data-science-visualization-assistant",  # Remove /tree/main for PyPI compatibility
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)