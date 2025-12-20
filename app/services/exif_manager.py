from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import os

class ExifManager:
    @staticmethod
    def get_exif_data(image_path):
        """
        Extracts and converts EXIF data into a readable dictionary.
        """
        exif_data = {}
        try:
            image = Image.open(image_path)
            info = image._getexif()
            if info:
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        exif_data[decoded] = gps_data
                    else:
                        # Convert bytes to string if needed for JSON serialization
                        if isinstance(value, bytes):
                            try:
                                value = value.decode()
                            except:
                                value = str(value)
                        exif_data[decoded] = value
        except Exception as e:
            print(f"Error extracting EXIF: {e}")
            pass
        return exif_data

    @staticmethod
    def remove_exif(source_path, dest_path=None):
        """
        Removes EXIF data and saves the image.
        If dest_path is None, overwrites source_path (or saves to a temporary location).
        Actually for typical web usage, we probably want to create a new 'purified' version.
        """
        if dest_path is None:
            # Create a prefixed filename
            dir_name, file_name = os.path.split(source_path)
            dest_path = os.path.join(dir_name, f"purified_{file_name}")

        try:
            image = Image.open(source_path)
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            
            # Save without metadata
            image_without_exif.save(dest_path)
            return dest_path
        except Exception as e:
            print(f"Error purifying image: {e}")
            return None
    
    @staticmethod
    def modify_exif(source_path, changes, dest_path=None):
        """
        Modifies specific EXIF tags.
        'changes' is a dict of tag names (str) and new values (str).
        Supported keys in changes: 'Artist', 'Copyright', 'ImageDescription'
        """
        if dest_path is None:
            # For simplicity in this app, we might want to overwrite or create a new version.
            # Let's create a 'modified_' version to be safe.
            dir_name, file_name = os.path.split(source_path)
            if not file_name.startswith("formatted_"):
                 dest_path = os.path.join(dir_name, f"formatted_{file_name}")
            else:
                 dest_path = source_path

        try:
            image = Image.open(source_path)
            
            # Load existing EXIF or create new if missing
            if "exif" in image.info:
                exif_dict = piexif.load(image.info["exif"])
            else:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            # Map helper strings to piexif tags (Group, ID)
            # Group 0 = 0th, Group 1 = Exif
            tag_db = {
                'Artist': (0, piexif.ImageIFD.Artist),
                'Copyright': (0, piexif.ImageIFD.Copyright),
                'ImageDescription': (0, piexif.ImageIFD.ImageDescription),
                'Software': (0, piexif.ImageIFD.Software),
                'Make': (0, piexif.ImageIFD.Make),
                'Model': (0, piexif.ImageIFD.Model),
                'DateTime': (0, piexif.ImageIFD.DateTime),
                'HostComputer': (0, piexif.ImageIFD.HostComputer),
                'UserComment': (1, piexif.ExifIFD.UserComment),
                'LensMake': (1, piexif.ExifIFD.LensMake),
                'LensModel': (1, piexif.ExifIFD.LensModel),
                'BodySerialNumber': (1, piexif.ExifIFD.BodySerialNumber),
                'CameraOwnerName': (1, piexif.ExifIFD.CameraOwnerName)
            }

            for key, value in changes.items():
                if key in tag_db and value:
                    group_idx, tag_id = tag_db[key]
                    group_name = "0th" if group_idx == 0 else "Exif"
                    
                    # Encoding logic
                    if key == 'UserComment':
                        # UserComment has a special structure: 8 header bytes + value
                        # simpler way relying on library helper if possible, but piexif expects raw bytes usually
                        # Standard header: b'UNICODE\x00' + utf16 or just b'ASCII\x00\x00\x00'
                        # Simplified for this MVP: ASCII
                        encoded_val = b'ASCII\x00\x00\x00' + value.encode('ascii', 'ignore') 
                        exif_dict[group_name][tag_id] = encoded_val
                    else:
                        # Most text tags are ASCII/UTF-8 bytes null terminated essentially
                        exif_dict[group_name][tag_id] = value.encode('utf-8')

            exif_bytes = piexif.dump(exif_dict)
            image.save(dest_path, exif=exif_bytes)
            return dest_path
        except Exception as e:
            print(f"Error modifying EXIF: {e}")
            # Try saving without EXIF if it fails (fallback)
            try:
                image.save(dest_path)
            except:
                pass
            return None
