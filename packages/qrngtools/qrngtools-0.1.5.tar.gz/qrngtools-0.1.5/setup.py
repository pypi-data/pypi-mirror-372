from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="qrngtools",
    version="0.1.5",
    description="Quantum random number generation using IBM Quantum (Qiskit)",
    long_description=(here / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="INVINCIBLES",
    author_email="dvskartikeya@gmail.com",
    url="https://github.com/karthikeyadusi/qrngtools",  # Update with your repo URL
    license="AUCE",
    packages=find_packages(),
    install_requires=[
        "qiskit>=1.4.1",
        "qiskit-aer>=0.13.0",
        "qiskit-ibm-provider>=0.7.0"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "qrngtools=qrngtools.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",  # For early-stage/hackathon projects
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Security :: Cryptography",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
)
