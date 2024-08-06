from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .models import File, User
from . import db, app
import os

file_bp = Blueprint('file', __name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)
    
    new_file = File(filename=filename, filepath=filepath, owner_id=user_id)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({'message': 'File uploaded successfully'}), 201

@file_bp.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    files = [{'filename': file.filename, 'upload_time': file.upload_time} for file in user.files]
    return jsonify(files), 200

@file_bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    user_id = get_jwt_identity()
    file = File.query.filter_by(filename=filename, owner_id=user_id).first()
    
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    
    return jsonify({'message': 'File not found'}), 404

@file_bp.route('/delete/<filename>', methods=['DELETE'])
@jwt_required()
def delete_file(filename):
    user_id = get_jwt_identity()
    file = File.query.filter_by(filename=filename, owner_id=user_id).first()
    
    if file:
        os.remove(file.filepath)
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'}), 200

    return jsonify({'message': 'File not found'}), 404

app.register_blueprint(file_bp, url_prefix='/files')
