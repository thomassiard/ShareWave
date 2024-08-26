# **ShareWave**

[Fakultet informatike u Puli](https://fipu.unipu.hr)\
Kolegij: [Raspodijeljeni sustavi](https://fiputreca.notion.site/Raspodijeljeni-sustavi-544564d5cc9e48b3a38d4143216e5dd6)\
Nositelj kolegija: [doc.dr.sc. Nikola Tanković](https://www.notion.so/fiputreca/Kontakt-stranica-875574d1b92248b1a8e90dae52cd29a9)\
Student: Thomas Siard

## **Opis**

ShareWave je distribuirani sustav za dijeljenje datoteka razvijen u Pythonu koji koristi peer-to-peer mrežu za upravljanje torrent datotekama. Temelji se na distribuiranoj arhitekturi koja omogućava visoku skalabilnost i pouzdanost, pružajući korisnicima brz i siguran upload, pretraživanje i preuzimanje datoteka. Platforma uključuje ključne komponente kao što su tracker server za praćenje seeder-a i leechera, file handler za upravljanje datotekama, client i client handler za korisničko sučelje i komunikaciju, te definira protokole za interakciju između klijenata i trackera.

Projekt omogućava jednostavno upravljanje raznim vrstama datoteka (.txt, .csv, .pdf) kroz intuitivno CLI sučelje. U sklopu projekta postoji testni direktorij za provjeru funkcionalnosti. Glavni cilj je pokrenuti tracker server, otvoriti više terminala za klijente, i omogućiti im upload, download, pregled liste torrenta, pomoć i izlaz iz aplikacije. ShareWave pruža praktično rješenje za dijeljenje resursa u radnim skupinama, obrazovnim institucijama i istraživačkim timovima, omogućavajući učinkovito i pouzdano dijeljenje datoteka.

## **Test**

```bash
pytest -v src/test/run_tests.py
```

## **Tracker**

```bash
cd src
python tracker.py 8888
```

## **Client**

```bash
cd src
python client_handler.py 127.0.0.1 8881 127.0.0.1 8888
```