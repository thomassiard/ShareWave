from src.protocol import Protocol

class Torrent:
    def __init__(self, tid, filename, numPieces):
        self.tid = tid
        self.filename = filename
        self.numPieces = numPieces
        self.seeders = {}  # Pohranjuje seeder-e sa ključem PID i vrijednošću (IP, PORT)
        self.leechers = {}  # Pohranjuje leecher-e sa ključem PID i vrijednošću (IP, PORT)

    def addSeeder(self, pid, peer_ip, peer_port):
        """Dodaje seeder u listu seedera"""
        self.seeders[pid] = (peer_ip, peer_port)
        print(f"Added seeder: {pid} ({peer_ip}:{peer_port})")

    def addLeecher(self, pid, peer_ip, peer_port):
        """Dodaje leecher u listu leechera"""
        self.leechers[pid] = (peer_ip, peer_port)
        print(f"Added leecher: {pid} ({peer_ip}:{peer_port})")

    def getSeeders(self):
        """Vraća sve seedere"""
        return self.seeders

    def getLeechers(self):
        """Vraća sve leechere"""
        return self.leechers

    def getTorrentInfo(self):
        """Vraća informacije o torrentu uključujući seedere i leechere"""
        return {
            "tid": self.tid,
            "filename": self.filename,
            "numPieces": self.numPieces,
            "seeders": self.seeders,
            "leechers": self.leechers
        }

if __name__ == "__main__":
    # Primjer korištenja
    torrent = Torrent(tid=1, filename="example.txt", numPieces=10)

    # Dodavanje seedera
    torrent.addSeeder(pid="peer1", peer_ip="127.0.0.1", peer_port=8881)

    # Dodavanje leechera
    torrent.addLeecher(pid="peer2", peer_ip="127.0.0.1", peer_port=8882)

    # Dohvat svih seedera
    seeders = torrent.getSeeders()
    print("Seeders:", seeders)

    # Dohvat svih leechera
    leechers = torrent.getLeechers()
    print("Leechers:", leechers)

    # Dohvat svih informacija o torrentu
    torrent_info = torrent.getTorrentInfo()
    print("Torrent Info:", torrent_info)
