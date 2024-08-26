from setuptools import setup, find_packages

setup(
    name="ShareWave",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'requests==2.25.1',  # HTTP knjižnica za slanje zahtjeva
        'pyzmq==26.1.1',    # Python binding za ZeroMQ
        'tornado==6.4.1',   # Web okvir i asinkrono mrežno programiranje
    ],
    entry_points={
        "console_scripts": [
            "sharewave-tracker=tracker:main",  # CLI komanda za pokretanje tracker servera
            "sharewave-client=client_handler:main",  # CLI komanda za pokretanje klijentskog handlera
        ],
    },
    python_requires='>=3.6', 
    extras_require={
        'dev': [
            'pytest==6.2.5',   
            'coverage==5.5',  
            'tox==3.24.5', 
        ],
    },
)
