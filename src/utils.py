import os
import hashlib
import logging

# Postavljanje osnovnog logiranja
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dijeli datoteku na manje dijelove specificirane veličine chunk_size.
def split_file(filepath, chunk_size=1024):

    if not os.path.exists(filepath):
        logging.error(f"File {filepath} not found.")
        raise FileNotFoundError(f"File {filepath} not found.")
    
    parts = []
    with open(filepath, 'rb') as file:
        chunk = file.read(chunk_size)
        i = 0
        while chunk:
            part_filename = f'{filepath}_part{i}'
            with open(part_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            parts.append(part_filename)
            logging.info(f"Created chunk: {part_filename}")
            i += 1
            chunk = file.read(chunk_size)
    return parts

# Spaja dijelove datoteke natrag u jednu datoteku.
def combine_files(parts, output_path, delete_parts=False):

    with open(output_path, 'wb') as output_file:
        for part in parts:
            with open(part, 'rb') as file:
                output_file.write(file.read())
            logging.info(f"Added {part} to {output_path}")

    if delete_parts:
        delete_file_parts(parts)
        logging.info("Deleted file parts after combining.")
    
    return output_path

# Dohvaća i sortira dijelove datoteke iz direktorija.
def get_file_parts(filepath):

    directory, filename = os.path.split(filepath)
    parts = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith(filename) and '_part' in f]
    parts.sort()  # Osigurava da su dijelovi u ispravnom redoslijedu
    logging.info(f"Found parts: {parts}")
    return parts

# Briše dijelove datoteke s diska.
def delete_file_parts(parts):

    for part in parts:
        os.remove(part)
        logging.info(f"Deleted {part}")

# Izračunava SHA-256 hash datoteke za provjeru integriteta.
def calculate_file_hash(filepath):

    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    logging.info(f"Calculated hash for {filepath}: {file_hash}")
    return file_hash

# Izračunava optimalnu veličinu dijelova (chunkova) na temelju veličine datoteke i broja peerova.
def calculate_optimal_chunk_size(file_size, num_peers):

    optimal_chunk_size = max(1024, file_size // (num_peers * 2))
    logging.info(f"Optimal chunk size calculated: {optimal_chunk_size} bytes")
    return optimal_chunk_size

if __name__ == "__main__":
    # Primjer korištenja
    filepath = 'input/Industry.csv'

    # Provjera veličine datoteke
    file_size = os.path.getsize(filepath)
    chunk_size = calculate_optimal_chunk_size(file_size, num_peers=3)

    # Dijeljenje datoteke na dijelove
    parts = split_file(filepath, chunk_size)

    # Spajanje dijelova datoteke
    combined_path = 'output/combined_Industry.csv'
    combine_files(parts, combined_path, delete_parts=True)

    # Provjera integriteta
    original_hash = calculate_file_hash(filepath)
    combined_hash = calculate_file_hash(combined_path)
    
    if original_hash == combined_hash:
        logging.info("Integrity check passed. Files match.")
    else:
        logging.error("Integrity check failed. Files do not match.")
