from setuptools import setup, find_packages

setup(
    name="ShareWave",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # List your project dependencies here
        # For example:
        # 'requests>=2.25.1',
        # 'numpy>=1.19.2',
    ],
    entry_points={
        "console_scripts": [
            "sharewave-tracker=tracker:main",
            "sharewave-client=client_handler:main",
        ],
    },
    python_requires='>=3.6',  # Change this to the minimum Python version you support
)
