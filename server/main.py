from flask import Flask, request, jsonify
from models import File, User  # Importajte potrebne modele iz models.py datoteke

app = Flask(__name__)

# Pretvaranje podataka o datoteci u JSON format
def file_to_json(file):
    return {
        'file_id': file.file_id,
        'filename': file.filename,
        'size': file.size,
        'upload_date': file.upload_date
    }

# Simulacija baze podataka
files = []
users = []

@app.route('/upload', methods=['POST'])
def upload_file():
    # Pretvaranje podataka dobivenih iz zahtjeva u objekt datoteke
    file_id = len(files) + 1
    filename = request.form['filename']
    size = len(request.files['file'].read())
    upload_date = 'Today'  # Trebate implementirati logiku za dobivanje datuma
    new_file = File(file_id, filename, size, upload_date)

    # Dodavanje datoteke u listu datoteka
    files.append(new_file)

    # Vraćanje odgovora o uspješnom uploadu datoteke
    return jsonify({'message': 'File uploaded successfully', 'file': file_to_json(new_file)}), 200

@app.route('/search', methods=['GET'])
def search_file():
    query = request.args.get('query')
    # Implementirajte logiku pretraživanja datoteka na temelju upita

    search_results = [file_to_json(file) for file in files if query.lower() in file.filename.lower()]
    return jsonify({'message': 'Search results', 'results': search_results}), 200

@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    # Pronađite datoteku po ID-u
    file = next((file for file in files if file.file_id == file_id), None)
    if file:
        # Implementirajte logiku za preuzimanje datoteke
        return jsonify({'message': 'File downloaded successfully', 'file': file_to_json(file)}), 200
    else:
        return jsonify({'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
