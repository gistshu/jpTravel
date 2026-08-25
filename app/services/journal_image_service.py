import json
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.exceptions import ValidationError

MAX_JOURNAL_IMAGES = 5
MAX_RECOMMENDATION_IMAGES = 3
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_STORED_IMAGE_BYTES = 1024 * 1024
MAX_IMAGE_SIDE = 1600
UPLOAD_ROOT = Path("static/uploads/journals")


def parse_image_urls(value: str | None) -> list[str]:
    """Return a safe image URL list stored in the journal JSON text column."""
    if not value:
        return []

    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(decoded, list):
        return []

    return [item for item in decoded if isinstance(item, str)]


def dump_image_urls(image_urls: list[str]) -> str:
    """Serialize journal image URLs with stable UTF-8 JSON."""
    return json.dumps(image_urls, ensure_ascii=False)


async def build_journal_image_urls(
    existing_image_urls: list[str],
    uploads: list[UploadFile],
    max_images: int = MAX_JOURNAL_IMAGES,
) -> list[str]:
    """Compress uploaded journal images and return the full stored URL list."""
    cleaned_existing_urls = [
        image_url
        for image_url in existing_image_urls
        if image_url.startswith("/static/uploads/journals/")
    ]
    real_uploads = [upload for upload in uploads if upload.filename]

    if len(cleaned_existing_urls) + len(real_uploads) > max_images:
        raise ValidationError(f"圖片最多 {max_images} 張")

    saved_urls = []
    for upload in real_uploads:
        saved_urls.append(await _compress_and_save_upload(upload))

    return [*cleaned_existing_urls, *saved_urls]


async def _compress_and_save_upload(upload: UploadFile) -> str:
    content_type = upload.content_type or ""
    if not content_type.startswith("image/"):
        raise ValidationError("只能上傳圖片檔案")

    content = await upload.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValidationError("單張圖片不可超過 10MB")

    try:
        from io import BytesIO

        with Image.open(BytesIO(content)) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode not in {"RGB", "L"}:
                image = image.convert("RGB")

            UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
            filename = f"{uuid.uuid4().hex}.jpg"
            output_path = UPLOAD_ROOT / filename
            output_path.write_bytes(_encode_under_size_limit(image))
    except UnidentifiedImageError as exc:
        raise ValidationError("無法讀取圖片檔案") from exc

    return f"/static/uploads/journals/{filename}"


def _encode_under_size_limit(image: Image.Image) -> bytes:
    """Return JPEG bytes below the stored image size cap."""
    from io import BytesIO

    working_image = image.copy()
    encoded = b""
    for max_side in (MAX_IMAGE_SIDE, 1400, 1200, 1000, 800, 640, 480, 360, 320):
        working_image.thumbnail((max_side, max_side))
        for quality in (84, 78, 72, 66, 60, 54, 48, 42, 36):
            buffer = BytesIO()
            working_image.save(buffer, format="JPEG", quality=quality, optimize=True)
            encoded = buffer.getvalue()
            if len(encoded) <= MAX_STORED_IMAGE_BYTES:
                return encoded

    if len(encoded) > MAX_STORED_IMAGE_BYTES:
        raise ValidationError("圖片壓縮後仍超過 1MB，請選擇較小的圖片")
    return encoded
