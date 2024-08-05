# **ShareWave**

[Fakultet informatike u Puli](https://fipu.unipu.hr)\
Kolegij: [Raspodijeljeni sustavi](https://fiputreca.notion.site/Raspodijeljeni-sustavi-544564d5cc9e48b3a38d4143216e5dd6)\
Nositelj kolegija: [doc.dr.sc. Nikola Tanković](https://www.notion.so/fiputreca/Kontakt-stranica-875574d1b92248b1a8e90dae52cd29a9)\
Student: Thomas Siard

## **Opis**

ShareWave je platforma za dijeljenje datoteka koja omogućava brz i siguran pristup uploadu, pretraživanju i preuzimanju datoteka. Temelji se na distribuiranoj arhitekturi koja čini podatke dostupnima na različitim točkama mreže, pružajući visoku skalabilnost i otpornost na kvarove.

Jednostavno korisničko sučelje olakšava upload datoteka, a sigurnosni mehanizmi osiguravaju da samo ovlaštene osobe mogu pristupiti sadržaju. Intuitivno pretraživanje i organizacija metapodataka čine pronalaženje željenog sadržaja jednostavnim.

Ovaj projekt istražuje ključne koncepte raspodijeljenih sustava, poput horizontalnog skaliranja i decentralizirane pohrane podataka. ShareWave pruža praktično rješenje za dijeljenje resursa u radnim skupinama, obrazovnim institucijama ili istraživačkim timovima.

S jednostavnim iskustvom i inovativnim pristupom dijeljenju datoteka, ShareWave čini tehnologiju raspodijeljenih sustava dostupnom svima, pridonoseći efikasnijem i pristupačnijem dijeljenju resursa.

### **Postavljanje**

1. Klonirajte repozitorij: `git clone <repo-url>`
2. Instalirajte ovisnosti: `pip install -r requirements.txt`
3. Pokrenite aplikaciju: `uvicorn server.main:app --reload`


#### **Korištenje**

- **Upload datoteke:** `POST /files/`
- **Pretraživanje datoteka:** `GET /files/`
- **Preuzimanje datoteke:** `GET /files/{file_id}`
