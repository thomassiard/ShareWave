from torrent import Torrent
from protocol import FIELDS, OPT_GET_LIST, OPT_GET_TORRENT, OPT_START_SEED, OPT_STOP_SEED, OPT_UPLOAD_FILE, RET_SUCCESS, RET_FAIL, RET_ALREADY_SEEDING, RET_NO_AVAILABLE_TORRENTS, RET_TORRENT_DOES_NOT_EXIST, READ_SIZE
import asyncio
import json
import sys

class TrackerServer:
    def __init__(self):
        self.nextTorrentId = 0  # Sljedeći ID za novi torrent
        self.torrents = {}  # Rječnik za pohranu torrenta sa njihovim jedinstvenim ID-ovima

    def handleRequest(self, req) -> dict: # Obrada dolaznih zahtjeva od klijenata i vraćanje rječnika s odgovorom

        opc = req.get(FIELDS['OPC'])  # Dohvaća opciju iz zahtjeva
        response = {FIELDS['OPC']: opc}

        if opc == OPT_GET_LIST:
            # Dohvaća listu svih dostupnih torrenta
            torrents = self.getTorrentList()
            response[FIELDS['TORRENT_LIST']] = torrents if torrents else []  # Dodaje listu torrenta u odgovor
            response[FIELDS['RET']] = RET_SUCCESS if torrents else RET_NO_AVAILABLE_TORRENTS  # Postavlja status

        elif opc == OPT_GET_TORRENT:
            # Dohvaća specifične podatke o torrentu prema ID-u
            if req[FIELDS['TID']] not in self.torrents:
                response[FIELDS['RET']] = RET_TORRENT_DOES_NOT_EXIST  # Torrent ne postoji
            else:
                torrent = self.getTorrentObject(req)  # Dohvaća detalje o torrentu
                response[FIELDS['TORRENT']] = torrent  # Dodaje detalje u odgovor
                response[FIELDS['RET']] = RET_SUCCESS  # Postavlja status

        elif opc == OPT_START_SEED:
            # Ažurira status peera koji počinje dijeliti torrent
            response[FIELDS['RET']] = self.updatePeerStatus(req)  # Postavlja status operacije
            response[FIELDS['TID']] = req[FIELDS['TID']]  # Dodaje ID torrenta u odgovor

        elif opc == OPT_STOP_SEED:
            # Ažurira status peera koji prestaje dijeliti torrent
            response[FIELDS['RET']] = self.updateStopSeed(req)  # Postavlja status operacije

        elif opc == OPT_UPLOAD_FILE:
            # Dodaje novi torrent ako se šalje novi fajl
            status, tid = self.addNewFile(req)  # Dodaje novi torrent i dobiva status
            response[FIELDS['RET']] = status  # Postavlja status operacije
            response[FIELDS['TID']] = tid  # Dodaje ID novog torrenta u odgovor

        else:
            # Nevažeća opcija
            response[FIELDS['RET']] = RET_FAIL  # Postavlja status neuspjeha

        return response

    def getTorrentList(self) -> list: # Dohvaća listu svih torrenta dostupnih na trackeru
 
        return [
            {
                FIELDS['TID']: torrent.tid,  # ID torrenta
                FIELDS['FILE_NAME']: torrent.filename,  # Naziv fajla
                FIELDS['TOTAL_PIECES']: torrent.pieces,  # Ukupni broj dijelova
                FIELDS['SEEDER_LIST']: torrent.getSeeders(),  # Lista seeder-a
                FIELDS['LEECHER_LIST']: torrent.getLeechers()  # Lista leecher-a
            }
            for torrent in self.torrents.values()  # Iterira kroz sve torrente
        ]

    def getTorrentObject(self, req: dict) -> dict: # Dohvaća detalje o specifičnom torrentu prema ID-u
  
        torrent = self.torrents[req[FIELDS['TID']]]  # Dohvaća torrent prema ID-u
        torrentDict = {
            FIELDS['TID']: torrent.tid,  # ID torrenta
            FIELDS['FILE_NAME']: torrent.filename,  # Naziv fajla
            FIELDS['TOTAL_PIECES']: torrent.pieces,  # Ukupni broj dijelova
            FIELDS['SEEDER_LIST']: torrent.getSeeders(),  # Lista seeder-a
            FIELDS['LEECHER_LIST']: torrent.getLeechers()  # Lista leecher-a
        }
        # Dodaje peera kao leechera
        torrent.addLeecher(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])
        return torrentDict

    def updatePeerStatus(self, req: dict) -> int: # Ažurira status peera u listi seeder-a torrenta
  
        torrent = self.torrents.get(req[FIELDS['TID']])  # Dohvaća torrent prema ID-u
        if torrent:
            torrent.addSeeder(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])  # Dodaje peera kao seeder-a
            torrent.removeLeecher(req[FIELDS['PID']])  # Uklanja peera iz liste leecher-a
            return RET_SUCCESS  # Operacija uspješna
        return RET_FAIL  # Operacija neuspješna

    def updateStopSeed(self, req: dict) -> int: # Uklanja peera iz liste seeder-a za određeni torrent
   
        torrent = self.torrents.get(req[FIELDS['TID']])  # Dohvaća torrent prema ID-u
        if torrent:
            print("[TRACKER] Uklanjanje seeder-a:", req[FIELDS['PID']])  # Ispisuje informaciju o uklanjanju
            torrent.removeSeeder(req[FIELDS['PID']])  # Uklanja peera iz liste seeder-a
            self.checkSeedersList(req[FIELDS['TID']])  # Provjerava listu seeder-a
            return RET_SUCCESS  # Operacija uspješna
        return RET_FAIL  # Operacija neuspješna

    def checkSeedersList(self, tid): # Provjerava listu seeder-a za određeni torrent
 
        if not self.torrents[tid].seeders:  # Ako nema seeder-a
            self.torrents.pop(tid)  # Uklanja torrent iz rječnika
            self.nextTorrentId -= 1  # Smanjuje ID za novi torrent
            print(f"Ažurirana lista torrenta: {self.torrents}")  # Ispisuje ažuriranu listu

    def addNewFile(self, req: dict) -> tuple: # Dodaje novi torrent na tracker i vraća status i ID torrenta

        # Provjerava je li peer već seeder za neki torrent
        if any(req[FIELDS['PID']] in torrent.getSeeders() for torrent in self.torrents.values()):
            return RET_ALREADY_SEEDING, None  # Peer već seeder

        newTorrent = Torrent(self.nextTorrentId, req[FIELDS['FILE_NAME']], req[FIELDS['TOTAL_PIECES']])  # Stvara novi torrent
        newTorrent.addSeeder(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])  # Dodaje peera kao seeder-a
        self.torrents[self.nextTorrentId] = newTorrent  # Dodaje novi torrent u rječnik
        self.nextTorrentId += 1  # Povećava ID za novi torrent
        return RET_SUCCESS, newTorrent.tid  # Vraća status i ID novog torrenta

    async def receiveRequest(self, reader, writer): # Prima zahtjeve od klijenata, obrađuje ih i šalje nazad odgovore

        try:
            data = await reader.read(READ_SIZE)  # Čita podatke od klijenta
            request = json.loads(data.decode())  # Dekodira podatke u rječnik
            addr = writer.get_extra_info('peername')  # Dohvaća informacije o klijentu

            print(f"\n[TRACKER] Primljen zahtjev: {request} od {addr}")  # Ispisuje primljeni zahtjev

            response = self.handleRequest(request)  # Obradjuje zahtjev
            payload = json.dumps(response)  # Kodira odgovor u JSON format
            print(f"[TRACKER] Slanje odgovora: {payload}")  # Ispisuje odgovor

            writer.write(payload.encode())  # Šalje odgovor klijentu
            await writer.drain()  # Čeka da se podaci ispišu
        except Exception as e:
            print(f"Greška: {e}")  # Ispisuje grešku
            print(f"[TRACKER] Peer {writer.get_extra_info('peername')} se odspojio.")  # Ispisuje informaciju o disconektu
        finally:
            writer.close()  # Zatvara konekciju

def parseCommandLine(): # Parsira argumente komandne linije za dobivanje broja porta

    if len(sys.argv) != 2:
        print("Korištenje: tracker.py [port servera]")  # Ispisuje upute za korištenje
        return 8888  # Zadani port

    try:
        port = int(sys.argv[1])  # Pokušava konvertirati port u cijeli broj
        if 0 <= port <= 65535:
            return port  # Vraća port ako je u ispravnom rasponu
        else:
            print("Port mora biti između 0 i 65535.")  # Ispisuje grešku ako port nije u rasponu
            return 8888  # Zadani port
    except ValueError:
        print("Neispravan broj porta.")  # Ispisuje grešku ako port nije cijeli broj
        return 8888  # Zadani port

async def main():
    ip = '127.0.0.1'  # Koristi localhost za jednostavnost
    port = parseCommandLine()  # Dohvaća port iz komandne linije
    
    server = await asyncio.start_server(TrackerServer().receiveRequest, ip, port)  # Pokreće server
    addr = server.sockets[0].getsockname()  # Dohvaća adresu servera
    print(f'[TRACKER] Slušanje na {addr}')  # Ispisuje adresu servera

    async with server:
        await server.serve_forever()  # Održava server aktivnim

if __name__ == "__main__":
    asyncio.run(main())  # Pokreće main funkciju
