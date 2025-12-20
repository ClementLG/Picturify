from flask import jsonify, request, send_file, current_app
from app.api import api
from app.services.image_handler import ImageHandler
from app.services.exif_manager import ExifManager
import os
import random

def trigger_bg_cleanup():
    # Cleanup files older than configured age with configured probability
    prob = current_app.config.get('CLEANUP_PROBABILITY', 0.2)
    max_age = current_app.config.get('MAX_FILE_AGE_SECONDS', 3600)
    
    if random.random() < prob:
        ImageHandler.cleanup_old_files(max_age)

@api.route('/analyze', methods=['POST'])
def analyze():
    # Cleanup check
    trigger_bg_cleanup()
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    filename = ImageHandler.save_image(file)
    
    if not filename:
        return jsonify({'error': 'Invalid file'}), 400
        
    file_path = ImageHandler.get_path(filename)
    exif_data = ExifManager.get_exif_data(file_path)
    
    return jsonify({
        'filename': filename,
        'exif_data': exif_data
    })

@api.route('/purify', methods=['POST'])
def purify():
    # Cleanup check
    trigger_bg_cleanup()

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    filename = ImageHandler.save_image(file)
    
    if not filename:
        return jsonify({'error': 'Invalid file'}), 400
    
    file_path = ImageHandler.get_path(filename)
    purified_path = ExifManager.remove_exif(file_path)
    
    if purified_path:
        purified_filename = os.path.basename(purified_path)
        if purified_filename != filename:
            ImageHandler.delete_file(filename)
            
        return send_file(purified_path, mimetype='image/jpeg') 
    
    return jsonify({'error': 'Processing failed'}), 500
