import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import time

class ImageHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    @staticmethod
    def save_image(file):
        if not file or not ImageHandler.allowed_file(file.filename):
            return None
        
        filename = secure_filename(file.filename)
        # Create a unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(file_path)
            return unique_filename
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

    @staticmethod
    def get_path(filename):
        return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    @staticmethod
    def cleanup_old_files(max_age_seconds=3600):
        # This could be run as a background task
        upload_folder = current_app.config['UPLOAD_FOLDER']
        now = time.time()
        
        if not os.path.exists(upload_folder):
            return

        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < now - max_age_seconds:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing old file {filename}: {e}")
