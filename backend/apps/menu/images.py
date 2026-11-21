"""Shrink uploaded photos so the public site stays light on slow mobile connections."""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from PIL import Image, ImageOps

MAX_SIZE = 1600
JPEG_QUALITY = 82


def shrink_upload(fieldfile: FieldFile, max_size: int = MAX_SIZE) -> None:
    """Re-encode a newly uploaded image as an upright JPEG no larger than ``max_size``.

    Only touches files that haven't been stored yet, so re-saving a model leaves its
    existing photo alone. Phone photos arrive at 4000px+ and several MB; this brings
    them to roughly 150-300 KB.
    """
    if not fieldfile or getattr(fieldfile, "_committed", True):
        return
    with Image.open(fieldfile) as source:
        image = ImageOps.exif_transpose(source)
        image.thumbnail((max_size, max_size))
        if image.mode != "RGB":
            image = image.convert("RGB")
        buffer = BytesIO()
        image.save(buffer, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    name = f"{Path(fieldfile.name).stem}.jpg"
    fieldfile.save(name, ContentFile(buffer.getvalue()), save=False)
