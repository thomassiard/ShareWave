# src/protocol.py

# Opcije za komunikaciju sa serverom
# PEER 2 SERVER Opcije
OPT_GET_LIST = 10
OPT_GET_TORRENT = 11
OPT_START_SEED = 12
OPT_STOP_SEED = 13
OPT_UPLOAD_FILE = 14

# PEER 2 PEER Opcije
OPT_STATUS_INTERESTED = 1
OPT_STATUS_UNINTERESTED = 2
OPT_STATUS_CHOKED = 3
OPT_STATUS_UNCHOKED = 4
OPT_GET_PEERS = 5
OPT_GET_PIECE = 6

# Povratni kodovi
RET_FINISHED_SEEDING = 2
RET_FINISHED_DOWNLOAD = 1
RET_SUCCESS = 0
RET_FAIL = -1
RET_ALREADY_SEEDING = -2
RET_NO_AVAILABLE_TORRENTS = -3
RET_TORRENT_DOES_NOT_EXIST = -4

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
