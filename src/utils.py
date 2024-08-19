import os
import hashlib

def split_file(filepath, chunk_size=1024):

    parts = []
    with open(filepath, 'rb') as file:
        chunk = file.read(chunk_size)
        i = 0
        while chunk:
            part_filename = f'{filepath}_part{i}'
            with open(part_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            parts.append(part_filename)
            i += 1
            chunk = file.read(chunk_size)
    return parts

def combine_files(parts, output_path):

    with open(output_path, 'wb') as output_file:
        for part in parts:
            with open(part, 'rb') as file:
                output_file.write(file.read())
    return output_path

def get_file_parts(filepath):

    directory, filename = os.path.split(filepath)
    parts = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith(filename) and '_part' in f]
    parts.sort()  # Ensure parts are in correct order
    return parts

def delete_file_parts(parts):

    for part in parts:
        os.remove(part)

def calculate_file_hash(filepath):

    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    # Example usage
    filepath = 'src/input/sample.txt'

    # Split the file
    parts = split_file(filepath)

    # Combine the file parts
    combined_path = 'src/output/combined_sample.txt'
    combine_files(parts, combined_path)

    # Check integrity
    original_hash = calculate_file_hash(filepath)
    combined_hash = calculate_file_hash(combined_path)
    
    if original_hash == combined_hash:
        print("Integrity check passed. Files match.")
        # Optionally delete the parts after successful combination
        delete_file_parts(parts)
    else:
        print("Integrity check failed. Files do not match.")
