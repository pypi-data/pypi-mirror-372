from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='tcai-sandesh',
    version='1.0.0',
    description='AI-powered audio sentiment analyzer with a Flask-based web interface.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='The Celeritas AI',
    author_email='business@theceleritasai.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==3.0.2",
        "transformers==4.41.2",
        "torch==2.6.0",
        "speechrecognition==3.10.1",
        "pydub==0.25.1",
        "librosa==0.10.2",
        "matplotlib==3.8.4",
        "numpy==1.26.4",
    ],
    entry_points={
        'console_scripts': [
            'tcai-sandesh=tcai_sandesh.app:main',  # Entry point
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
