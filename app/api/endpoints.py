from flask import jsonify, request, send_file
from app.api import api
from app.services.image_handler import ImageHandler
from app.services.exif_manager import ExifManager
import os

@api.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    filename = ImageHandler.save_image(file)
    
    if not filename:
        return jsonify({'error': 'Invalid file'}), 400
        
    file_path = ImageHandler.get_path(filename)
    exif_data = ExifManager.get_exif_data(file_path)
    
    # Cleanup immediately for API calls? Or rely on background task? 
    # For now, keep it to allow potential subsequent operations, or just return data.
    
    return jsonify({
        'filename': filename,
        'exif_data': exif_data
    })

@api.route('/purify', methods=['POST'])
def purify():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    filename = ImageHandler.save_image(file)
    
    if not filename:
        return jsonify({'error': 'Invalid file'}), 400
    
    file_path = ImageHandler.get_path(filename)
    purified_path = ExifManager.remove_exif(file_path)
    
    if purified_path:
        return send_file(purified_path, mimetype='image/jpeg') # Simplification: assuming mime type or detecting it
    
    return jsonify({'error': 'Processing failed'}), 500
