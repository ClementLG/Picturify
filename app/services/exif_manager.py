from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import os
import logging
import shutil
from flask import current_app


logger = logging.getLogger(__name__)

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
            logger.error(f"Error extracting EXIF: {e}")
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
            
            # We strip metadata by simply saving the image to a new file.
            # PIL does not preserve EXIF by default when saving, so we just need to re-save it.
            # This avoids the incredibly expensive list(image.getdata()) operation.
            
            # Note: We must explicitly handle potential rotation if it was EXIF-based? 
            # The 'purify' action implies stripping ALL metadata, so native orientation is expected.
            
            image.save(
                dest_path, 
                quality=current_app.config['IMAGE_QUALITY'], 
                subsampling=current_app.config['IMAGE_SUBSAMPLING']
            )
            return dest_path
        except Exception as e:
            logger.error(f"Error purifying image: {e}")
            return None
    
    @staticmethod
    def get_lat_lon(exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data."""
        lat = None
        lon = None

        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]

            gps_latitude = gps_info.get("GPSLatitude")
            gps_latitude_ref = gps_info.get("GPSLatitudeRef")
            gps_longitude = gps_info.get("GPSLongitude")
            gps_longitude_ref = gps_info.get("GPSLongitudeRef")

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = ExifManager._convert_to_degrees(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = -lat

                lon = ExifManager._convert_to_degrees(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = -lon
        return lat, lon

    @staticmethod
    def _convert_to_degrees(value):
        """
        Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
        """
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    
    @staticmethod
    def _convert_to_dms(value):
        """
        Helper function to convert float degrees to EXIF DMS format (rational tuples).
        """
        value = abs(value)
        d = int(value)
        m = int((value - d) * 60)
        s = (value - d - m/60) * 3600
        # return tuples of (numerator, denominator)
        # precision: 1/100 for seconds
        return ((d, 1), (m, 1), (int(s * 100), 100))

    @staticmethod
    def modify_exif(source_path, changes, dest_path=None):
        """
        Modifies specific EXIF tags.
        'changes' is a dict of tag names (str) and new values (str).
        Now supports 'gps_lat' and 'gps_lon' (floats/strings).
        """
        if dest_path is None:
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

            for key, value in changes.items():
                if not value: continue
                # ... GPS Handling ...
                if key == 'gps_lat':
                    try:
                        lat = float(value)
                        ref = 'N' if lat >= 0 else 'S'
                        dms = ExifManager._convert_to_dms(lat)
                        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = dms
                        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = ref.encode('ascii')
                    except Exception as e:
                        logger.error(f"Error processing GPS Lat: {e}")
                    continue
                
                if key == 'gps_lon':
                    try:
                        lon = float(value)
                        ref = 'E' if lon >= 0 else 'W'
                        dms = ExifManager._convert_to_dms(lon)
                        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = dms
                        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = ref.encode('ascii')
                    except Exception as e:
                        logger.error(f"Error processing GPS Lon: {e}")
                    continue

                group, tag_id = ExifManager._find_tag_info(key)
                
                if group and tag_id:
                    if key == 'UserComment':
                         encoded_val = b'ASCII\x00\x00\x00' + value.encode('ascii', 'ignore')
                         exif_dict[group][tag_id] = encoded_val
                    else:
                        tag_type = piexif.TAGS["Image" if group == "0th" else group][tag_id]["type"]
                        if tag_type == piexif.TYPES.Ascii:
                            exif_dict[group][tag_id] = value.encode('utf-8')
                        elif tag_type == piexif.TYPES.Undefined:
                             exif_dict[group][tag_id] = value.encode('utf-8')
                        else:
                            try:
                                if tag_type in [piexif.TYPES.Short, piexif.TYPES.Long]:
                                    exif_dict[group][tag_id] = int(value)
                                else:
                                    logger.debug(f"Skipping complex tag {key} (Type {tag_type})")
                            except Exception:
                                pass

            exif_bytes = piexif.dump(exif_dict)
            image.save(
                dest_path, 
                exif=exif_bytes, 
                quality=current_app.config['IMAGE_QUALITY'], 
                subsampling=current_app.config['IMAGE_SUBSAMPLING']
            )
            return dest_path

        except Exception as e:
            logger.error(f"Error modifying EXIF: {e}")
            return None

    @staticmethod
    def delete_tags(source_path, tags_to_delete, dest_path=None):
        """
        Removes specific EXIF tags from the image.
        """
        if dest_path is None:
            dir_name, file_name = os.path.split(source_path)
            if not file_name.startswith("formatted_"):
                 dest_path = os.path.join(dir_name, f"formatted_{file_name}")
            else:
                 dest_path = source_path

        try:
            image = Image.open(source_path)
            
            if "exif" in image.info:
                exif_dict = piexif.load(image.info["exif"])
            else:
                # No EXIF to delete
                return dest_path

            for tag_name in tags_to_delete:
                group, tag_id = ExifManager._find_tag_info(tag_name)
                if group and tag_id:
                    if tag_id in exif_dict[group]:
                        del exif_dict[group][tag_id]
            
            exif_bytes = piexif.dump(exif_dict)
            image.save(
                dest_path, 
                exif=exif_bytes, 
                quality=current_app.config['IMAGE_QUALITY'], 
                subsampling=current_app.config['IMAGE_SUBSAMPLING']
            )
            return dest_path
        except Exception as e:
            logger.error(f"Error deleting EXIF tags: {e}")
            return None

    @staticmethod
    def keep_only_tags(source_path, kept_tags, dest_path=None):
        """
        Removes all EXIF tags EXCEPT those in kept_tags.
        kept_tags is a list of tag names (str).
        """
        if dest_path is None:
            dir_name, file_name = os.path.split(source_path)
            # Use 'optimized_' prefix to distinguish
            if not file_name.startswith("optimized_"):
                 dest_path = os.path.join(dir_name, f"optimized_{file_name}")
            else:
                 dest_path = source_path

        try:
            image = Image.open(source_path)
            
            if "exif" in image.info:
                try:
                    exif_dict = piexif.load(image.info["exif"])
                except Exception:
                    return None
            else:
                return dest_path

            # Helper to check if a tag should be kept
            def should_keep(group_name, tag_id):
                # Get tag name
                try:
                    if group_name == "0th":
                        tag_name = piexif.TAGS["Image"][tag_id]["name"]
                    elif group_name == "Exif":
                        tag_name = piexif.TAGS["Exif"][tag_id]["name"]
                    elif group_name == "GPS":
                         tag_name = piexif.GPSTAGS[tag_id] # GPSTAGS is direct dict ID->Name
                    else:
                        return False # remove 1st/Interop if not explicitly handled
                    
                    return tag_name in kept_tags
                except KeyError:
                    return False

            # Iterate and Filter...
            # Note: We repeat the logic here for clarity, though it's the same pattern
            new_0th = {}
            for tag_id, val in exif_dict["0th"].items():
                if should_keep("0th", tag_id):
                    new_0th[tag_id] = val
            exif_dict["0th"] = new_0th

            new_exif = {}
            for tag_id, val in exif_dict["Exif"].items():
                if should_keep("Exif", tag_id):
                    new_exif[tag_id] = val
            exif_dict["Exif"] = new_exif

            new_gps = {}
            for tag_id, val in exif_dict["GPS"].items():
                if should_keep("GPS", tag_id):
                    new_gps[tag_id] = val
            exif_dict["GPS"] = new_gps

            exif_dict["1st"] = {} 
            exif_dict["thumbnail"] = None 

            exif_bytes = piexif.dump(exif_dict)
            image.save(
                dest_path, 
                exif=exif_bytes, 
                quality=current_app.config['IMAGE_QUALITY'], 
                subsampling=current_app.config['IMAGE_SUBSAMPLING']
            )
            return dest_path

        except Exception as e:
            logger.error(f"Error optimizing EXIF tags: {e}")
            return None

    @staticmethod
    def _find_tag_info(tag_name):
        """
        Helper to find which IFD group and ID a tag string belongs to.
        Returns (group_name, tag_id)
        """
        # Check 0th IFD (Image)
        for tag_id, name in piexif.TAGS["Image"].items():
            if name["name"] == tag_name:
                return "0th", tag_id
        # Check Exif IFD
        for tag_id, name in piexif.TAGS["Exif"].items():
            if name["name"] == tag_name:
                return "Exif", tag_id
        # Check GPS
        for tag_id, name in piexif.GPSTAGS.items():
            if name == tag_name:
                return "GPS", tag_id
                
        return None, None
