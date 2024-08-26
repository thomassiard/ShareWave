from protocol import *
import base64

# Definira se kodiranje koje će se koristiti za rad s tekstom
ENCODING = 'utf-8'

def encodeToBytes(file_name: str):
    """
    Učitaj datoteku i kodiraj je u nizove bajtova koristeći Base64 kodiranje.
    
    :param file_name: Ime datoteke koju treba kodirati
    :return: Tuple s popisom kodiranih dijelova i brojem dijelova
    """
    pieces = []  # Lista kodiranih dijelova
    numPieces = 0  # Broj dijelova
    
    with open(file_name, "rb") as input_file:
        piece = input_file.read(PIECE_SIZE)
        while piece:
            numPieces += 1
            encodedPiece = base64.b64encode(piece)  # Kodiraj dio u Base64
            hexPiece = encodedPiece.decode(ENCODING)  # Pretvori kodirani dio u string
            pieces.append(hexPiece)
            piece = input_file.read(PIECE_SIZE)  # Učitaj sljedeći dio
            
    return pieces, numPieces

def decodeToFile(pieces: list, output_name: str):
    """
    Dekodiraj nizove bajtova kodirane u Base64 i upiši ih u datoteku.
    
    :param pieces: Lista kodiranih dijelova
    :param output_name: Ime datoteke u koju će se upisati dekodirani podaci
    """
    with open(output_name, "wb") as output_file:
        for block in pieces:
            encodedBlock = block.encode(ENCODING)  # Pretvori string u bytes
            decodedBlock = base64.b64decode(encodedBlock)  # Dekodiraj iz Base64
            output_file.write(decodedBlock)  # Upisuj u izlaznu datoteku

# TESTIRANJE:
# pieces, numPieces = encodeToBytes("./files/sample.txt")
# print(numPieces)
# decodeToFile(pieces, "./files/output.txt")

# pieces, numPieces = encodeToBytes("./files/sfu_sample.png")
# print(numPieces)
# decodeToFile(pieces, "./files/sfu_output.png")
