from setuptools import setup, find_packages

setup(
    name="ShareWave",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'atomicwrites==1.4.1',  # Biblioteka za pisanje u atomskom režimu, često korišćena u testiranju
        'attrs==24.2.0',        # Količinska knjižnica za rad sa atributima objekata
        'certifi==2024.7.4',    # Pruža sertifikate za HTTPS konekcije
        'chardet==4.0.0',       # Automatsko otkrivanje enkodiranja karaktera
        'colorama==0.4.6',      # Omogućava obojene terminalske ispisne podatke
        'docopt==0.6.2',        # Parser komandne linije za dokumentaciju
        'idna==2.10',           # Internacionalizovani domeni
        'iniconfig==2.0.0',     # Očitanje i pisanje konfiguracija u INI formatu
        'packaging==24.1',      # Alati za rad sa verzijama i pakovanjima
        'pluggy==0.13.1',       # Sistem za ugradnju dodataka (plug-in)
        'py==1.11.0',           # Različite pomoćne funkcije za Python
        'pure-eval==0.2.3',     # Evaluacija izraza u čistom Pythonu
        'pywin32==306',         # Windows specifične ekstenzije za Python
        'pyzmq==26.1.1',        # Python bindings za ZeroMQ
        'requests==2.25.1',     # HTTP biblioteka za jednostavno slanje HTTP zahteva
        'six==1.16.0',          # Pomoćna biblioteka za rad sa Python 2 i 3
        'stack-data==0.6.3',    # Alat za rad sa podacima o steku
        'toml==0.10.2',         # Parsiranje TOML formata
        'tornado==6.4.1',       # Web server i asinkroni mrežni okvir
        'traitlets==5.14.3',    # Konfiguracija i upravljanje atributima objekata
        'urllib3==1.26.19',    # HTTP biblioteka za Python koja se koristi za rad sa URL-ovima
        'webencodings==0.5.1',  # Encoding za rad sa web fontovima i karakterima
        'yarg==0.1.9',          # Alat za parsiranje komandnih linija
    ],
    # Definirane komandne skripte koje će biti dostupne u CLI
    entry_points={
        "console_scripts": [
            "sharewave-tracker=tracker:main",
            "sharewave-client=client_handler:main",  
        ],
    },
    python_requires='>=3.6',
)
