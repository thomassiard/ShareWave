import base64
import os
import logging

# Postavljanje osnovnog logger-a za zapisivanje u fajl
log_dir = 'src/logs'
log_file = 'file_handler.log'
log_path = os.path.join(log_dir, log_file)

# Kreirajte log folder ako ne postoji
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Konfiguracija osnovnog logovanja
logging.basicConfig(filename=log_path,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

PIECE_SIZE = 64 * 1024  # 64 KB
ENCODING = 'utf-8'

def encodeToBytes(file_name: str):
    pieces = []
    numPieces = 0
    try:
        with open(file_name, "rb") as input_file:
            piece = input_file.read(PIECE_SIZE)
            while piece:
                numPieces += 1
                encodedPiece = base64.b64encode(piece)
                hexPiece = encodedPiece.decode(ENCODING)
                pieces.append(hexPiece)
                piece = input_file.read(PIECE_SIZE)
        logging.info(f"Encoded file {file_name} into {numPieces} pieces.")
    except FileNotFoundError:
        logging.error(f"File not found: {file_name}")
    except Exception as e:
        logging.error(f"Error encoding file {file_name}: {e}")
    return pieces, numPieces

def decodeToFile(pieces: list, output_name: str):
    try:
        with open(output_name, "wb") as output_file:
            for block in pieces:
                encodedBlock = block.encode(ENCODING)
                decodedBlock = base64.b64decode(encodedBlock)
                output_file.write(decodedBlock)
        logging.info(f"Decoded {len(pieces)} pieces to file {output_name}.")
    except Exception as e:
        logging.error(f"Error decoding to file {output_name}: {e}")

# TESTING:
if __name__ == "__main__":
    # Test encoding and decoding with sample files
    sample_files = [
        ("./files/sample.txt", "./files/output.txt"),
        ("./files/sfu_sample.png", "./files/sfu_output.png")
    ]

    for input_file, output_file in sample_files:
        pieces, num_pieces = encodeToBytes(input_file)
        print(f"Number of pieces: {num_pieces}")
        decodeToFile(pieces, output_file)
        print(f"File {input_file} processed to {output_file}.")
