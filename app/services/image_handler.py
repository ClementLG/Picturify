import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app
import time
from PIL import Image


logger = logging.getLogger(__name__)

import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

class ImageHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    @staticmethod
    def save_image(file):
        if not file or not ImageHandler.allowed_file(file.filename):
            return None
        
        # Basic Magic Number Check (Skipped for HEIC as imghdr doesn't support it well)
        # We rely on PIL to verify it later
        
        ImageHandler.enforce_storage_limit()
        
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        
        # Create a unique filename
        unique_id = uuid.uuid4().hex
        
        if ext in ['heic', 'heif']:
            # Convert to JPG
            filename = f"{filename.rsplit('.', 1)[0]}.jpg"
            unique_filename = f"{unique_id}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                # Save temp heic
                temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{unique_id}_temp.{ext}")
                file.save(temp_path)
                
                with Image.open(temp_path) as img:
                    img.convert('RGB').save(file_path, 'JPEG', quality=95)
                
                # Remove temp file
                os.remove(temp_path)
                
            except Exception as e:
                logger.error(f"Error converting HEIC: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
        else:
            unique_filename = f"{unique_id}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(file_path)
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                return None

        # Deep Verification using PIL
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            logger.error(f"Invalid image file (PIL verification failed): {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return None

        return unique_filename

    @staticmethod
    def get_path(filename):
        # Prevent Path Traversal by enforcing secure_filename
        return os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))

    @staticmethod
    def delete_file(filename):
        if not filename: return
        file_path = ImageHandler.get_path(filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {e}")

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
                os.remove(files[i])
            except Exception as e:
                logger.error(f"Error removing old file {files[i]}: {e}")

    @staticmethod
    def cleanup_old_files(max_age_seconds=3600):
        """
        Removes files older than max_age_seconds.
        Optimized to avoid scanning thousands of files on every request.
        """
        upload_folder = current_app.config['UPLOAD_FOLDER']
        now = time.time()
        
        if not os.path.exists(upload_folder):
            return

        # Optimization: Don't scan ALL files every time.
        # Scan a random subset or stop after deleting a few?
        # A simple approach for synchronous web requests is to limit the scan.
        try:
             # Just listdir can be slow if directory is huge, but it's the fastest way to get handles.
            files = os.listdir(upload_folder)
            
            # If we have too many files, just check a random sample of them (e.g. 50)
            # This ensures we don't block for long even if there are 10,000 files.
            # Over time, everything gets cleaned.
            import random
            if len(files) > 50:
                files = random.sample(files, 50)
                
            for filename in files:
                file_path = os.path.join(upload_folder, filename)
                # Ensure we only check files
                if os.path.isfile(file_path):
                    try:
                        # cached stat call?
                        if os.stat(file_path).st_mtime < now - max_age_seconds:
                            os.remove(file_path)
                    except OSError:
                        pass # File might have been deleted by another thread/process
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
