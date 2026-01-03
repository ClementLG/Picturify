from flask import render_template, request, redirect, url_for, flash, current_app, send_file
from app.main import main
from app.services.image_handler import ImageHandler
from app.services.exif_manager import ExifManager
from app.services.metadata_templates import MetadataTemplates
import os
import random

def trigger_bg_cleanup():
    # Cleanup files older than configured age with configured probability
    prob = current_app.config.get('CLEANUP_PROBABILITY', 0.2)
    max_age = current_app.config.get('MAX_FILE_AGE_SECONDS', 3600)
    
    if random.random() < prob:
        ImageHandler.cleanup_old_files(max_age)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Cleanup check
        trigger_bg_cleanup()

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

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/result/<filename>')
def result(filename):
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    exif_data = ExifManager.get_exif_data(file_path)
    
    # Calculate Lat/Lon for Map
    lat, lon = ExifManager.get_lat_lon(exif_data)
    
    # Check for specific interesting fields
    gps_info = exif_data.get('GPSInfo')
    
    trigger_download = request.args.get('download') == 'true'
    
    return render_template('result.html', filename=filename, exif_data=exif_data, gps_info=gps_info, lat=lat, lon=lon, trigger_download=trigger_download, template_list=MetadataTemplates.list_templates())

@main.route('/download/<filename>')
def download(filename):
    file_path = ImageHandler.get_path(filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@main.route('/delete_selected/<filename>', methods=['POST'])
def delete_selected(filename):
    trigger_bg_cleanup()
    file_path = ImageHandler.get_path(filename)
    if not file_path or not os.path.exists(file_path):
        flash("File not found.")
        return redirect(url_for('main.index'))
    
    selected_tags = request.form.getlist('selected_tags')
    
    if selected_tags:
        modified_path = ExifManager.delete_tags(file_path, selected_tags)
        if modified_path:
             modified_filename = os.path.basename(modified_path)
             if modified_filename != filename:
                 ImageHandler.delete_file(filename)
             flash(f"Deleted {len(selected_tags)} tags successfully.")
             return redirect(url_for('main.result', filename=modified_filename))
        else:
             flash("Error deleting tags.")
    else:
        flash("No tags selected.")
    
    return redirect(url_for('main.result', filename=filename))

@main.route('/purify/<filename>', methods=['POST'])
def purify(filename):
    trigger_bg_cleanup()
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    purified_path = ExifManager.remove_exif(file_path)
    if purified_path:
        purified_filename = os.path.basename(purified_path)
        if purified_filename != filename:
            ImageHandler.delete_file(filename)

        # Redirect to result with download trigger
        return redirect(url_for('main.result', filename=purified_filename, download='true'))
    
    flash('Error processing file')
    return redirect(url_for('main.result', filename=filename))

@main.route('/apply_template/<filename>', methods=['POST'])
def apply_template(filename):
    trigger_bg_cleanup()
    file_path = ImageHandler.get_path(filename)
    if not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('main.index'))
    
    template_name = request.form.get('template_name')
    if not template_name:
        flash('No template selected')
        return redirect(url_for('main.result', filename=filename))
        
    kept_tags = MetadataTemplates.get_template(template_name)
    if not kept_tags:
        flash('Invalid template')
        return redirect(url_for('main.result', filename=filename))
        
    optimized_path = ExifManager.keep_only_tags(file_path, kept_tags)
    
    if optimized_path:
        optimized_filename = os.path.basename(optimized_path)
        if optimized_filename != filename:
            ImageHandler.delete_file(filename)
            
        flash(f'Metadata optimized for {template_name.capitalize()}!')
        return redirect(url_for('main.result', filename=optimized_filename))
        
    flash('Error processing file with template')
    return redirect(url_for('main.result', filename=filename))

@main.route('/finish/<filename>', methods=['POST'])
def finish(filename):
    ImageHandler.delete_file(filename)
    flash('Session finished. File cleanup completed.')
    return redirect(url_for('main.index'))

@main.route('/edit/<filename>', methods=['POST'])
def edit(filename):
    trigger_bg_cleanup()
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
        if modified_filename != filename:
            ImageHandler.delete_file(filename)
            
        flash('Metadata updated successfully!')
        return redirect(url_for('main.result', filename=modified_filename))
    
    flash('Error updating metadata')
    return redirect(url_for('main.result', filename=filename))
