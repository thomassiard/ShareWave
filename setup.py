from setuptools import setup, find_packages

setup(
    name="ShareWave",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'atomicwrites==1.4.1',
        'attrs==24.2.0',
        'certifi==2024.7.4',
        'chardet==4.0.0',
        'colorama==0.4.6',
        'idna==2.10',
        'iniconfig==2.0.0',
        'packaging==24.1',
        'pluggy==0.13.1',
        'py==1.11.0',
        'pytest==6.2.4',
        'requests==2.25.1',
        'setuptools==72.2.0',
        'toml==0.10.2',
        'urllib3==1.26.19'
    ],
    entry_points={
        "console_scripts": [
            "sharewave-tracker=tracker:main",
            "sharewave-client=client_handler:main",
        ],
    },
    python_requires='>=3.6',
)
