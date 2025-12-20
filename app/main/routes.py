from flask import render_template, request, redirect, url_for, flash, current_app, send_file
from app.main import main
from app.services.image_handler import ImageHandler
from app.services.exif_manager import ExifManager
import os

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        filename = ImageHandler.save_image(file)
        if filename:
            return redirect(url_for('main.result', filename=filename))
        else:
            flash('Invalid file type or save error')
            return redirect(request.url)

    return render_template('index.html')

@main.route('/result/<filename>')
def result(filename):
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    exif_data = ExifManager.get_exif_data(file_path)
    
    # Check for specific interesting fields
    gps_info = exif_data.get('GPSInfo')
    
    return render_template('result.html', filename=filename, exif_data=exif_data, gps_info=gps_info)

@main.route('/download/<filename>')
def download(filename):
    file_path = ImageHandler.get_path(filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@main.route('/purify/<filename>', methods=['POST'])
def purify(filename):
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    purified_path = ExifManager.remove_exif(file_path)
    if purified_path:
        # For simplicity, we redirect to download the purified file directly or show a success page
        # Here lets redirect to a download of the *new* file
        purified_filename = os.path.basename(purified_path)
        return redirect(url_for('main.download', filename=purified_filename))
    
    flash('Error processing file')
    return redirect(url_for('main.result', filename=filename))

@main.route('/edit/<filename>', methods=['POST'])
def edit(filename):
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    # Collect form data
    # We iterate over the form to allow dynamic custom fields
    changes = {}
    
    # Predefined known keys are handled directly, but actually we can just take everything 
    # as the ExifManager filters by its 'tag_db' anyway.
    for key, value in request.form.items():
        if value and key not in ['csrf_token']: # exclude internal flask-wtf tokens if any
             # Map form names (lowercase) to Titular Case if needed? 
             # Actually our form will send correct keys like 'Artist' or 'Model'
             # For the hardcoded inputs in the template, we need to make sure they match the tag_db keys.
             # In prev step we had 'artist', 'copyright'. Let's normalize or fix the template.
             # Better strategy: Fix the template to send 'Artist', 'Copyright' as names.
             changes[key] = value

    # Fix case for default fields if they come in lowercase (backward compatibility)
    if 'artist' in changes: changes['Artist'] = changes.pop('artist')
    if 'copyright' in changes: changes['Copyright'] = changes.pop('copyright')
    if 'description' in changes: changes['ImageDescription'] = changes.pop('description')
    
    # Defaults
    if 'Software' not in changes:
        changes['Software'] = 'Picturify'
    
    modified_path = ExifManager.modify_exif(file_path, changes)
    
    if modified_path:
        modified_filename = os.path.basename(modified_path)
        flash('Metadata updated successfully!')
        return redirect(url_for('main.result', filename=modified_filename))
    
    flash('Error updating metadata')
    return redirect(url_for('main.result', filename=filename))
