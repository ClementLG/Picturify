from flask import render_template, request, redirect, url_for, flash, current_app, send_file, session
from app.main import main
from app.services.image_handler import ImageHandler
from app.services.exif_manager import ExifManager
from app.services.metadata_templates import MetadataTemplates
import os
import random

def trigger_bg_cleanup():
    # Reduce default probability to 10% to prevent frequent blocking
    prob = current_app.config.get('CLEANUP_PROBABILITY', 0.1)
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
        
        files = request.files.getlist('image')
        
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Enforce Batch Limit
        max_batch = current_app.config.get('MAX_BATCH_SIZE', 10)
        if len(files) > max_batch:
            flash(f'Too many files selected. Maximum is {max_batch}.')
            return redirect(request.url)
            
        saved_filenames = []
        for file in files:
            if file and file.filename != '':
                filename = ImageHandler.save_image(file)
                if filename:
                    saved_filenames.append(filename)
        
        if not saved_filenames:
            flash('No valid files saved.')
            return redirect(request.url)

        if len(saved_filenames) == 1 and not session.get('batch_files'):
            return redirect(url_for('main.result', filename=saved_filenames[0]))
        else:
            current_batch = session.get('batch_files', [])
            
            # Check if appending would exceed the limit
            if len(current_batch) + len(saved_filenames) > max_batch:
                # Delete newly uploaded files since we can't add them
                for f in saved_filenames:
                    ImageHandler.delete_file(f)
                flash(f'Cannot add files. total batch size would exceed {max_batch}.')
                return redirect(url_for('main.batch_result'))
                
            session['batch_files'] = current_batch + saved_filenames
            return redirect(url_for('main.batch_result'))

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
    
    changes = {}
    
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

# --- Batch Routes ---

@main.route('/batch_result')
def batch_result():
    filenames = session.get('batch_files', [])
    if not filenames:
        flash('No active batch.')
        return redirect(url_for('main.index'))
    
    valid_files = [f for f in filenames if os.path.exists(ImageHandler.get_path(f))]
    
    if len(valid_files) != len(filenames):
         session['batch_files'] = valid_files
         filenames = valid_files

    if not filenames:
         flash('All files in batch have been deleted.')
         return redirect(url_for('main.index'))

    return render_template('batch_results.html', filenames=filenames, template_list=MetadataTemplates.list_templates())

@main.route('/batch_action', methods=['POST'])
def batch_action():
    filenames = session.get('batch_files', [])
    action = request.form.get('action')
    
    if not filenames:
        flash('No batch to process.')
        return redirect(url_for('main.index'))

    processed_count = 0
    
    if action == 'purify':
        new_filenames = []
        for fname in filenames:
            file_path = ImageHandler.get_path(fname)
            if not os.path.exists(file_path): continue
            
            purified_path = ExifManager.remove_exif(file_path)
            if purified_path:
                new_fname = os.path.basename(purified_path)
                if new_fname != fname:
                    ImageHandler.delete_file(fname)
                new_filenames.append(new_fname)
                processed_count += 1
            else:
                new_filenames.append(fname)
        session['batch_files'] = new_filenames
        flash(f'Purified {processed_count} images.')

    elif action.startswith('template_'):
        template_name = action.replace('template_', '')
        kept_tags = MetadataTemplates.get_template(template_name)
        
        if kept_tags:
            new_filenames = []
            for fname in filenames:
                file_path = ImageHandler.get_path(fname)
                if not os.path.exists(file_path): continue
                
                optimized_path = ExifManager.keep_only_tags(file_path, kept_tags)
                if optimized_path:
                    new_fname = os.path.basename(optimized_path)
                    if new_fname != fname:
                         ImageHandler.delete_file(fname)
                    new_filenames.append(new_fname)
                    processed_count += 1
                else:
                    new_filenames.append(fname)
            session['batch_files'] = new_filenames
            flash(f'Optimized {processed_count} images for {template_name}.')
    
    return redirect(url_for('main.batch_result'))

@main.route('/download_batch', methods=['POST'])
def download_batch():
    filenames = session.get('batch_files', [])
    if not filenames:
        flash('No files to download.')
        return redirect(url_for('main.index'))

    import zipfile
    import io

    # Create in-memory zip
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            file_path = ImageHandler.get_path(fname)
            if os.path.exists(file_path):
                zf.write(file_path, arcname=fname)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='picturify_batch.zip'
    )

@main.route('/delete_batch_file/<filename>', methods=['POST'])
def delete_batch_file(filename):
    current_batch = session.get('batch_files', [])
    if filename in current_batch:
        current_batch.remove(filename)
        session['batch_files'] = current_batch
        ImageHandler.delete_file(filename)
        flash(f'Removed {filename}')
    else:
        flash('File not in batch')
    
    return redirect(url_for('main.batch_result'))

@main.route('/clear_batch', methods=['POST'])
def clear_batch():
    """Removes all files in the current batch from disk and session."""
    current_batch = session.get('batch_files', [])
    for fname in current_batch:
        ImageHandler.delete_file(fname)
    
    session.pop('batch_files', None)
    flash('Batch cleared and files deleted.')
    return redirect(url_for('main.index'))
