# api/utils.py
import uuid
import os

def upload_operator_file(instance, filename):
    from django.conf import settings

    folder = os.path.join(settings.MEDIA_ROOT, 'operators')
    if not os.path.exists(folder):
        os.makedirs(folder)

    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('operators', filename)