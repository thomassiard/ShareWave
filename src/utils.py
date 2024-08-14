import os

def split_file(filepath, chunk_size=1024):
    with open(filepath, 'rb') as file:
        chunk = file.read(chunk_size)
        i = 0
        while chunk:
            with open(f'{filepath}_part{i}', 'wb') as chunk_file:
                chunk_file.write(chunk)
            i += 1
            chunk = file.read(chunk_size)

def combine_files(parts, output_path):
    with open(output_path, 'wb') as output_file:
        for part in parts:
            with open(part, 'rb') as file:
                output_file.write(file.read())

if __name__ == "__main__":
    # Example usage
    split_file('src/input/sample.txt')
    combine_files(['src/input/sample.txt_part0'], 'src/output/combined_sample.txt')
