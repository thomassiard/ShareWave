from src.torrent import Torrent

# Kreiranje novog torrent objekta
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
