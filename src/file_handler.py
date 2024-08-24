import base64
import os

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
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except Exception as e:
        print(f"Error encoding file {file_name}: {e}")
    return pieces, numPieces

def decodeToFile(pieces: list, output_name: str):
    try:
        with open(output_name, "wb") as output_file:
            for block in pieces:
                encodedBlock = block.encode(ENCODING)
                decodedBlock = base64.b64decode(encodedBlock)
                output_file.write(decodedBlock)
    except Exception as e:
        print(f"Error decoding to file {output_name}: {e}")

# TESTING:
if __name__ == "__main__":
    pieces, numPieces = encodeToBytes("./files/sample.txt")
    print(f"Number of pieces: {numPieces}")
    decodeToFile(pieces, "./files/output.txt")

    pieces, numPieces = encodeToBytes("./files/sfu_sample.png")
    print(f"Number of pieces: {numPieces}")
    decodeToFile(pieces, "./files/sfu_output.png")
