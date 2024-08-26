from protocol import FIELDS

class Torrent: # Klasa koja predstavlja svaki torrent pohranjen na trackeru

    def __init__(self, tid, filename, numPieces):
        self.tid = tid  # ID torrenta
        self.filename = filename  # Ime datoteke
        self.pieces = numPieces  # Broj dijelova datoteke
        self.seeders = {}  # Rječnik za pohranu seeder-a
        self.leechers = {}  # Rječnik za pohranu leecher-a

    def addSeeder(self, pid: str, peer_ip: str, peer_port: int): # Metoda za dodavanje seedera u rječnik seedera

        self.seeders[pid] = {
            FIELDS['IP']: peer_ip,
            FIELDS['PORT']: peer_port
        }

    def removeSeeder(self, pid: str): # Metoda za uklanjanje seedera iz rječnika seedera

        if pid in self.seeders:
            del self.seeders[pid]

    def addLeecher(self, pid: str, peer_ip: str, peer_port: int): # Metoda za dodavanje leecher-a u rječnik leechera

        self.leechers[pid] = {
            FIELDS['IP']: peer_ip,
            FIELDS['PORT']: peer_port
        }

    def removeLeecher(self, pid: str): # Metoda za uklanjanje leecher-a iz rječnika leechera

        if pid in self.leechers:
            del self.leechers[pid]

    def getSeeders(self) -> dict: # Metoda za dohvaćanje svih seedera

        return self.seeders

    def getLeechers(self) -> dict: # Metoda za dohvaćanje svih leecher-a

        return self.leechers
