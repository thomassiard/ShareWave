from torrent import Torrent
from protocol import FIELDS, OPT_GET_LIST, OPT_GET_TORRENT, OPT_START_SEED, OPT_STOP_SEED, OPT_UPLOAD_FILE, RET_SUCCESS, RET_FAIL, RET_ALREADY_SEEDING, RET_NO_AVAILABLE_TORRENTS, RET_TORRENT_DOES_NOT_EXIST, READ_SIZE
import asyncio
import json
import sys

class TrackerServer:
    def __init__(self):
        self.nextTorrentId = 0  # Sljedeći ID za novi torrent
        self.torrents = {}  # Rječnik za pohranu torrenta sa njihovim jedinstvenim ID-ovima

    def handleRequest(self, req) -> dict:
        """
        Obradjuje dolazne zahtjeve od klijenata i vraća rječnik s odgovorom.
        """
        opc = req.get(FIELDS['OPC'])  # Dohvaća opciju iz zahtjeva
        response = {FIELDS['OPC']: opc}

        if opc == OPT_GET_LIST:
            # Dohvaća listu svih dostupnih torrenta
            torrents = self.getTorrentList()
            response[FIELDS['TORRENT_LIST']] = torrents if torrents else []
            response[FIELDS['RET']] = RET_SUCCESS if torrents else RET_NO_AVAILABLE_TORRENTS

        elif opc == OPT_GET_TORRENT:
            # Dohvaća specifične podatke o torrentu prema ID-u
            if req[FIELDS['TID']] not in self.torrents:
                response[FIELDS['RET']] = RET_TORRENT_DOES_NOT_EXIST
            else:
                torrent = self.getTorrentObject(req)
                response[FIELDS['TORRENT']] = torrent
                response[FIELDS['RET']] = RET_SUCCESS

        elif opc == OPT_START_SEED:
            # Ažurira status peera koji počinje dijeliti torrent
            response[FIELDS['RET']] = self.updatePeerStatus(req)
            response[FIELDS['TID']] = req[FIELDS['TID']]

        elif opc == OPT_STOP_SEED:
            # Ažurira status peera koji prestaje dijeliti torrent
            response[FIELDS['RET']] = self.updateStopSeed(req)

        elif opc == OPT_UPLOAD_FILE:
            # Dodaje novi torrent ako se šalje novi fajl
            status, tid = self.addNewFile(req)
            response[FIELDS['RET']] = status
            response[FIELDS['TID']] = tid

        else:
            # Nevažeća opcija
            response[FIELDS['RET']] = RET_FAIL

        return response

    def getTorrentList(self) -> list:
        """
        Vraća listu svih torrenta dostupnih na trackeru.
        """
        return [
            {
                FIELDS['TID']: torrent.tid,
                FIELDS['FILE_NAME']: torrent.filename,
                FIELDS['TOTAL_PIECES']: torrent.pieces,
                FIELDS['SEEDER_LIST']: torrent.getSeeders(),
                FIELDS['LEECHER_LIST']: torrent.getLeechers()
            }
            for torrent in self.torrents.values()
        ]

    def getTorrentObject(self, req: dict) -> dict:
        """
        Vraća detaljne informacije o specifičnom torrentu na temelju njegovog ID-a.
        """
        torrent = self.torrents[req[FIELDS['TID']]]
        torrentDict = {
            FIELDS['TID']: torrent.tid,
            FIELDS['FILE_NAME']: torrent.filename,
            FIELDS['TOTAL_PIECES']: torrent.pieces,
            FIELDS['SEEDER_LIST']: torrent.getSeeders(),
            FIELDS['LEECHER_LIST']: torrent.getLeechers()
        }
        # Dodaje peera kao leechera
        torrent.addLeecher(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])
        return torrentDict

    def updatePeerStatus(self, req: dict) -> int:
        """
        Ažurira status peera u listi seeder-a torrenta.
        """
        torrent = self.torrents.get(req[FIELDS['TID']])
        if torrent:
            torrent.addSeeder(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])
            torrent.removeLeecher(req[FIELDS['PID']])
            return RET_SUCCESS
        return RET_FAIL

    def updateStopSeed(self, req: dict) -> int:
        """
        Uklanja peera iz liste seeder-a za određeni torrent.
        """
        torrent = self.torrents.get(req[FIELDS['TID']])
        if torrent:
            print("[TRACKER] Uklanjanje seeder-a:", req[FIELDS['PID']])
            torrent.removeSeeder(req[FIELDS['PID']])
            self.checkSeedersList(req[FIELDS['TID']])
            return RET_SUCCESS
        return RET_FAIL

    def checkSeedersList(self, tid):
        """
        Provjerava ima li torrent još uvijek seeder-e, i ako nema, uklanja torrent iz rječnika.
        """
        if not self.torrents[tid].seeders:
            self.torrents.pop(tid)  # Uklanja torrent iz rječnika
            self.nextTorrentId -= 1
            print(f"Ažurirana lista torrenta: {self.torrents}")

    def addNewFile(self, req: dict) -> tuple:
        """
        Dodaje novi torrent na tracker. Vraća status i novi ID torrenta.
        """
        # Provjerava je li peer već seeder za neki torrent
        if any(req[FIELDS['PID']] in torrent.getSeeders() for torrent in self.torrents.values()):
            return RET_ALREADY_SEEDING, None

        newTorrent = Torrent(self.nextTorrentId, req[FIELDS['FILE_NAME']], req[FIELDS['TOTAL_PIECES']])
        newTorrent.addSeeder(req[FIELDS['PID']], req[FIELDS['IP']], req[FIELDS['PORT']])
        self.torrents[self.nextTorrentId] = newTorrent
        self.nextTorrentId += 1
        return RET_SUCCESS, newTorrent.tid

    async def receiveRequest(self, reader, writer):
        """
        Prima zahtjeve od klijenata, obrađuje ih i šalje nazad odgovore.
        """
        try:
            data = await reader.read(READ_SIZE)  # Čita podatke od klijenta
            request = json.loads(data.decode())  # Dekodira podatke u rječnik
            addr = writer.get_extra_info('peername')

            print(f"\n[TRACKER] Primljen zahtjev: {request} od {addr}")

            response = self.handleRequest(request)  # Obradjuje zahtjev
            payload = json.dumps(response)  # Kodira odgovor u JSON format
            print(f"[TRACKER] Slanje odgovora: {payload}")

            writer.write(payload.encode())  # Šalje odgovor klijentu
            await writer.drain()  # Čeka da se podaci ispišu
        except Exception as e:
            print(f"Greška: {e}")
            print(f"[TRACKER] Peer {writer.get_extra_info('peername')} se odspojio.")
        finally:
            writer.close()  # Zatvara konekciju

def parseCommandLine():
    """
    Parsira argumente komandne linije za dobivanje broja porta.
    """
    if len(sys.argv) != 2:
        print("Korištenje: tracker.py [port servera]")
        return 8888

    try:
        port = int(sys.argv[1])
        if 0 <= port <= 65535:
            return port
        else:
            print("Port mora biti između 0 i 65535.")
            return 8888
    except ValueError:
        print("Neispravan broj porta.")
        return 8888

async def main():
    ip = '127.0.0.1'  # Koristi localhost za jednostavnost
    port = parseCommandLine()
    
    server = await asyncio.start_server(TrackerServer().receiveRequest, ip, port)  # Pokreće server
    addr = server.sockets[0].getsockname()
    print(f'[TRACKER] Slušanje na {addr}')

    async with server:
        await server.serve_forever()  # Održava server aktivnim

if __name__ == "__main__":
    asyncio.run(main())
