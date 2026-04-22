import os
import uuid
from werkzeug.utils import secure_filename
from google.cloud import storage

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def upload_family_photo(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    original_name = secure_filename(file_storage.filename)
    unique_name = f"family/{uuid.uuid4().hex}_{original_name}"

    blob = bucket.blob(unique_name)
    blob.upload_from_file(
        file_storage,
        content_type=file_storage.content_type
    )
    return f"https://storage.googleapis.com/{bucket.name}/{blob.name}"