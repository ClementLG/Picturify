import os

class Config:
    # Secret key for session signing
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Directory where uploaded files are temporarily stored
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')

    # Max upload size (150 MB)
    MAX_CONTENT_LENGTH = 150 * 1024 * 1024

    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'webp', 'heic', 'heif'}

    # Maximum number of files to keep in storage before cleanup triggers
    MAX_STORED_FILES = 100

    # Maximum number of files a user can upload in a single batch session
    MAX_BATCH_SIZE = 10

    # Probability (0-1) that a cleanup run triggers on a request
    CLEANUP_PROBABILITY = 0.5

    # How old a file must be (in seconds) to be considered for deletion
    MAX_FILE_AGE_SECONDS = 600

    # Output quality for re-encoded images (1-100).
    # 100 = Best quality, 85-95 = Good balance.
    IMAGE_QUALITY = 100

    # Image Processing: Chroma subsampling (0-2).
    # 0 = 4:4:4 (Best, keeps all color info), 1 = 4:2:2, 2 = 4:2:0 (Standard JPEG).
    IMAGE_SUBSAMPLING = 0

    @staticmethod
    def init_app(app):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
