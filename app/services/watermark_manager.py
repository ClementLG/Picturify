from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class WatermarkManager:
    @staticmethod
    def apply_watermark(source_path, text, position='center', opacity=0.5, dest_path=None):
        """
        Applies a text watermark to the image.
        """
        if dest_path is None:
            dir_name, file_name = os.path.split(source_path)
            dest_path = os.path.join(dir_name, f"watermarked_{file_name}")

        try:
            with Image.open(source_path) as base:
                # Capture EXIF data before converting
                exif_data = base.info.get("exif")
                
                base = base.convert("RGBA")
                # Make a blank image for the text, initialized to transparent text color
                txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

                # font setup
                # Load font
                try:
                     # Use a large font size relative to image height (e.g., 5%)
                    font_size = int(base.size[1] * 0.05)
                    if font_size < 10: font_size = 10
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()

                d = ImageDraw.Draw(txt)
                
                # Calculate text dimensions
                left, top, right, bottom = d.textbbox((0, 0), text, font=font)
                text_width = right - left
                text_height = bottom - top
                
                # Calculate coordinates
                width, height = base.size
                x, y = 0, 0
                padding = int(width * 0.02) # 2% padding

                if position == 'center':
                    x = (width - text_width) / 2
                    y = (height - text_height) / 2
                elif position == 'bottom-right':
                    x = width - text_width - padding
                    y = height - text_height - padding
                elif position == 'bottom-left':
                    x = padding
                    y = height - text_height - padding
                elif position == 'top-right':
                    x = width - text_width - padding
                    y = padding
                elif position == 'top-left':
                    x = padding
                    y = padding

                # Draw text on the transparent layer
                alpha = int(255 * opacity)
                d.text((x, y), text, font=font, fill=(255, 255, 255, alpha))

                out = Image.alpha_composite(base, txt)

                # Save as RGB (removing alpha channel)
                save_kwargs = {
                    "quality": current_app.config['IMAGE_QUALITY'],
                    "subsampling": current_app.config['IMAGE_SUBSAMPLING']
                }
                
                if exif_data:
                    save_kwargs["exif"] = exif_data

                out.convert("RGB").save(dest_path, **save_kwargs)
                
                return dest_path
        except Exception as e:
            logger.error(f"Error applying watermark: {e}")
            return None
