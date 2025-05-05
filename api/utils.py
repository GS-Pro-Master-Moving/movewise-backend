# api/utils.py
import uuid
import os

#operator images to avoid lambda functions
def upload_operator_photo(instance, filename):
    from django.conf import settings
    folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'photos')
    os.makedirs(folder, exist_ok=True)
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('operators', 'photos', filename)


def upload_operator_license_front(instance, filename):
    from django.conf import settings
    folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'licenses', 'front')
    os.makedirs(folder, exist_ok=True)
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('operators', 'licenses', 'front', filename)


def upload_operator_license_back(instance, filename):
    from django.conf import settings
    folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'licenses', 'back')
    os.makedirs(folder, exist_ok=True)
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('operators', 'licenses', 'back', filename)

#order images
def upload_evidence_file(instance, filename):
    from django.conf import settings

    folder = os.path.join(settings.MEDIA_ROOT, 'evidences')
    if not os.path.exists(folder):
        os.makedirs(folder)

    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('evidences', filename)

#dispatch tickect image
def _upload_dispatch_file(instance, filename):
    from django.conf import settings

    folder = os.path.join(settings.MEDIA_ROOT, 'dispatch_tickets')
    if not os.path.exists(folder):
        os.makedirs(folder)

    ext = filename.split('.')[-1]
    short_uuid = str(uuid.uuid4()).split('-')[0]
    filename = f"{short_uuid}.{ext}"
    return os.path.join('dispatch_tickets', filename)
