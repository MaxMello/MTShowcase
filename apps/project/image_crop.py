import json
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile

from apps.project.models import UploadImage


def crop_image_and_save(file_path, crop_data):
    f = BytesIO()
    try:
        img_crop_data = crop_data
        img = Image.open(file_path)
        print("OPENED")
        img_crop = img.crop((
            int(img_crop_data["x"]),
            int(img_crop_data["y"]),
            int(img_crop_data["x"] + img_crop_data["width"]),
            int(img_crop_data["y"] + img_crop_data["height"]))
        )
        img_crop.save(f, format='PNG')
        img_crop_file = ContentFile(f.getvalue(), "content_image.png")
        return UploadImage.objects.create(file=img_crop_file)

    except Exception as e:
        # fallback just save not cropped image
        saved_file, existing = UploadImage.objects.get_or_create(file=file_path)
        print("Failed to open or crop image " + str(e))
        return saved_file
    finally:
        f.close()
