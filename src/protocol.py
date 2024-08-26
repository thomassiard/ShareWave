# Opcije za komunikaciju sa serverom

# PEER 2 SERVER Opcije
OPT_GET_LIST = 10              # Opcija za dobivanje popisa torrenta
OPT_GET_TORRENT = 11           # Opcija za preuzimanje torrenta
OPT_START_SEED = 12            # Opcija za početak dijeljenja (seeding)
OPT_STOP_SEED = 13             # Opcija za zaustavljanje dijeljenja (seeding)
OPT_UPLOAD_FILE = 14           # Opcija za upload nove datoteke

# PEER 2 PEER Opcije
OPT_STATUS_INTERESTED = 1      # Status interesiranosti
OPT_STATUS_UNINTERESTED = 2    # Status neinteresiranosti
OPT_STATUS_CHOKED = 3          # Status choked (blokiran)
OPT_STATUS_UNCHOKED = 4        # Status unchoked (otvoren)
OPT_GET_PEERS = 5              # Opcija za dobivanje liste peera
OPT_GET_PIECE = 6              # Opcija za dobivanje dijela datoteke

# Povratni kodovi
RET_FINISHED_SEEDING = 2       # Povratni kod za završeno dijeljenje (seeding)
RET_FINISHED_DOWNLOAD = 1      # Povratni kod za završeno preuzimanje (download)
RET_SUCCESS = 0                # Povratni kod za uspjeh
RET_FAIL = -1                  # Povratni kod za neuspjeh
RET_ALREADY_SEEDING = -2       # Povratni kod za već započeto dijeljenje (seeding)
RET_NO_AVAILABLE_TORRENTS = -3 # Povratni kod za nedostupne torente
RET_TORRENT_DOES_NOT_EXIST = -4 # Povratni kod za nepostojeći torrent

# Ključevi za polja u payloadu
FIELDS = {
    'OPC': 'OPC',                     # Opcija zahtjeva
    'RET': 'RET',                     # Povratni kod
    'IP': 'IP_ADDRESS',              # IP adresa
    'PORT': 'PORT',                  # Port
    'PID': 'PEER_ID',                # ID peera
    'TID': 'TORRENT_ID',             # ID torrenta
    'FILE_NAME': 'FILE_NAME',        # Ime datoteke
    'TOTAL_PIECES': 'NUM_OF_PIECES', # Broj dijelova datoteke
    'TORRENT_LIST': 'TORRENT_LIST',  # Lista torrenta
    'TORRENT': 'TORRENT_OBJ',        # Objekat torrenta
    'PIECE_IDX': 'PIECE_IDX',        # Indeks dijela
    'PIECE_DATA': 'PIECE_DATA',      # Podaci o dijelu
    'PEER_LIST': 'PEER_LIST',        # Lista peera
    'SEEDER_LIST': 'SEEDER_LIST',    # Lista seeder-a
    'LEECHER_LIST': 'LEECHER_LIST'   # Lista leecher-a
}

# Konstantne veličine
READ_SIZE = 24576  # Veličina čitanja u bajtovima (24KB)
PIECE_SIZE = 16384  # Veličina dijela u bajtovima (16KB)
