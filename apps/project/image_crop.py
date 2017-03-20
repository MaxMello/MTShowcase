import json
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile

from apps.project.models import ProjectUploadContentFile


def crop_image_and_save(project, file_path, crop_data, visiblity):
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
        return ProjectUploadContentFile.objects.create(project=project, file=img_crop_file, visible=visiblity)

    except Exception as e:
        # fallback just save not cropped image
        saved_file, created = ProjectUploadContentFile.objects.get_or_create(project=project, file=file_path)
        if not created:
            saved_file.visible = visiblity
            saved_file.save()
        print("Failed to open or crop image " + str(e))
        return saved_file
    finally:
        f.close()


def crop_compress_save_title_image(project_object, original, crop_data):
    f = BytesIO()
    try:
        if crop_data:
            img = Image.open(project_object.project_image.path)
            img_crop = img.crop((
                int(crop_data["x"]),
                int(crop_data["y"]),
                int(crop_data["x"] + crop_data["width"]),
                int(crop_data["y"] + crop_data["height"]))
            )

            width, height = img_crop.size
            if width >= 1280 and height >= 720:
                img_crop = img_crop.resize((1280, 720), Image.ANTIALIAS)

            img_crop.save(f, quality=95, optimize=True, format='PNG')
            img_crop_file = ContentFile(f.getvalue(), "croppedimage.png")
            project_object.project_image_cropped = img_crop_file
            project_object.save()

        f = BytesIO()
        project_img = Image.open(original)
        project_card_max_width = 500

        if project_img.size[0] >= 500:
            wpercent = (project_card_max_width / float(project_img.size[0]))
            hsize = int((float(project_img.size[1]) * float(wpercent)))

            img_resized = project_img.resize((project_card_max_width, hsize), Image.ANTIALIAS)
            img_resized.save(f, quality=95, optimize=True, format='PNG')
            project_img_file = ContentFile(f.getvalue(), "projectimageresize.png")
            project_object.project_image = project_img_file
            project_object.save()

    except Exception as e:
        print("-------------------------------------")
        print("Failed to open and crop image " + str(e))
        print("-------------------------------------")
    finally:
        f.close()
