# models.py

class File:
    def __init__(self, file_id, filename, size, upload_date):
        self.file_id = file_id
        self.filename = filename
        self.size = size
        self.upload_date = upload_date

class User:
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email
