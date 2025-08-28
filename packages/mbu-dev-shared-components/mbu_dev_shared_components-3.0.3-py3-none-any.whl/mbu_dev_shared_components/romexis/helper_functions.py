"""
Helper functions for working with exporting images from Romexis.
"""
import os
import zipfile
import shutil
import rawpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


def zip_folder_contents(folder_path: str, zip_filename: str) -> None:
    """
    Zips all files in the specified folder (non-recursive) into a .zip archive.

    Args:
        folder_path (str): Path to the folder containing files to zip.
        zip_filename (str): Full path (including .zip filename) for the output zip file.
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for filename in os.listdir(folder_path):
                full_path = os.path.join(folder_path, filename)
                if os.path.isfile(full_path):
                    zipf.write(full_path, arcname=filename)
    except Exception as e:
        print(f"Error zipping folder: {e}")
        raise


def add_black_bar_and_text_to_image(
    source_path: str,
    destination_path: str,
    patient_id: str,
    patient_name: str,
    optaget_dato: str,
    image_type: int,
    gamma_value: float,
    rotation_angle: int = 0,
    is_mirror: bool = False,
):
    """
    Adds a black box at the bottom of an image containing two lines of text:
    Patient name : patient id and optaget_dato.

    :param source_path: Path to the input image.
    :param patient_id: Value to display for the "Patient ID".
    :param optaget_dato: Value to display for the "Optaget dato".
    :param out_path: Path to save the resulting image.
    :param margin_x: Horizontal margin for the text inside the black box.
    """
    try:
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        filename = os.path.basename(source_path)
        copied_path = os.path.join(destination_path, filename)

        shutil.copy2(source_path, copied_path)

        try:
            with rawpy.imread(copied_path) as raw:
                # image_type 1 = Panorama
                if image_type == 1:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        gamma=(gamma_value, 1),
                        no_auto_scale=True,
                        dcb_enhance=False,
                        half_size=False,
                        demosaic_algorithm=None,
                        four_color_rgb=False,
                        use_auto_wb=False
                    )
                # image_type 2 = Cephalostat
                elif image_type == 2:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        gamma=(1, 1),
                        no_auto_scale=True,
                        dcb_enhance=False,
                        half_size=False,
                        demosaic_algorithm=None,
                        four_color_rgb=False,
                        use_auto_wb=False
                    )
                else:
                    # image_type 3 = Interoralt, image_type 4 = Foto
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        gamma=(gamma_value, 1),
                        no_auto_scale=True,
                        dcb_enhance=False,
                        half_size=False,
                        demosaic_algorithm=None,
                        four_color_rgb=False,
                        use_auto_wb=False
                    )
        except Exception as e:
            rgb = Image.open(copied_path).convert("RGB")
            rgb = np.array(rgb)

        image = Image.fromarray(rgb)

        if rotation_angle != 0:
            image = image.rotate(rotation_angle, expand=True)

        if is_mirror:
            image = ImageOps.mirror(image)

        width, height = image.size

        base_font_size = max(24, height // 30)
        font = ImageFont.truetype("arial.ttf", base_font_size)

        line1 = f"{patient_id} : {patient_name}"
        line2 = optaget_dato

        temp_image = Image.new('RGB', (width, height))
        draw_temp = ImageDraw.Draw(temp_image)

        def get_text_dimensions(text, font):
            bbox = draw_temp.textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

        line1_width, line1_height = get_text_dimensions(line1, font)
        line2_width, line2_height = get_text_dimensions(line2, font)

        margin_y = max(10, height // 50)
        spacing_between_lines = max(5, height // 80)
        black_box_height = line1_height + line2_height + spacing_between_lines + 2 * margin_y
        new_height = height + black_box_height

        new_image = Image.new('RGB', (width, new_height), color=(255, 255, 255))
        new_image.paste(image, (0, 0))

        draw = ImageDraw.Draw(new_image)
        box_top = new_height - black_box_height
        draw.rectangle([(0, box_top), (width, new_height)], fill="black")

        text_x = 5
        text_y = box_top + margin_y
        draw.text((text_x, text_y), line1, font=font, fill=(255, 255, 255))
        text_y += line1_height + spacing_between_lines
        draw.text((text_x, text_y), line2, font=font, fill=(255, 255, 255))

        if image_type == 4:
            final_path = copied_path.replace(".img", ".jpg")
            new_image.save(final_path, format="JPEG")
        else:
            final_path = copied_path.replace(".img", ".tiff")
            new_image.save(final_path, format='TIFF')

        print(f"Saved modified image at: {final_path}")

    except Exception as e:
        print(f"Error processing image: {e}")
        raise
