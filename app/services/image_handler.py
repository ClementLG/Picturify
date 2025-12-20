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
        
        ImageHandler.enforce_storage_limit()
        
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
    def delete_file(filename):
        if not filename: return
        file_path = ImageHandler.get_path(filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")

    @staticmethod
    def enforce_storage_limit():
        upload_folder = current_app.config['UPLOAD_FOLDER']
        max_files = current_app.config.get('MAX_STORED_FILES', 100)
        
        if not os.path.exists(upload_folder):
            return

        # List all files with full path
        files = []
        for f in os.listdir(upload_folder):
            fp = os.path.join(upload_folder, f)
            if os.path.isfile(fp):
                files.append(fp)
        
        # If we are strictly below or equal limit, do nothing
        if len(files) < max_files:
            return
            
        # Sort by modification time (oldest first)
        files.sort(key=os.path.getmtime)
        
        # Calculate how many to remove. 
        # We want to remove enough so that after adding 1 new file, we are still within limit.
        # But broadly, if current >= max, remove (current - max + 1)
        num_to_remove = len(files) - max_files + 1
        
        for i in range(num_to_remove):
            try:
                os.remove(files[i])
                print(f"Removed old file: {files[i]} due to storage limit.")
            except Exception as e:
                print(f"Error removing old file {files[i]}: {e}")

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
