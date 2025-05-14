# api/utils.py (versión unificada)
import os
import uuid
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# =====================================================================
# Función centralizada para rutas S3/DO Spaces (solo si USE_S3=True)
# =====================================================================
def get_s3_file_path(instance, filename, folder):
    """
    Genera rutas organizadas para S3/DO Spaces con estructura:
    media/companies/<company_id>/<folder>/<uuid>_<timestamp>.<ext>
    """
    ext = filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}_{int(timezone.now().timestamp())}.{ext}"
    
    # Obtener company_id desde el modelo
    company_id = None
    if hasattr(instance, 'id_company_id'):
        company_id = instance.id_company_id
    elif hasattr(instance, 'person') and hasattr(instance.person, 'id_company_id'):
        company_id = instance.person.id_company_id
    
    # Construir ruta final con prefijo 'media/'
    base_path = 'media'  
    if company_id:
        return os.path.join(base_path, 'companies', str(company_id), folder, unique_filename)
    else:
        return os.path.join(base_path, folder, unique_filename)

# =====================================================================
# Funciones para Operadores (Operator)
# =====================================================================
def upload_operator_photo(instance, filename):
    """Sube fotos de operadores a S3 o almacenamiento local"""
    if settings.USE_S3:
        logger.debug("Subiendo foto a S3/DO Spaces")
        return get_s3_file_path(instance, filename, 'operators/photos')
    else:
        logger.debug("Subiendo foto a almacenamiento local")
        local_folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'photos')
        os.makedirs(local_folder, exist_ok=True)
        ext = filename.split('.')[-1]
        unique_name = f"{uuid.uuid4()}.{ext}"
        return os.path.join('operators', 'photos', unique_name)

def upload_operator_license_front(instance, filename):
    """Sube frente de licencia a S3 o local"""
    if settings.USE_S3:
        return get_s3_file_path(instance, filename, 'operators/licenses/front')
    else:
        local_folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'licenses', 'front')
        os.makedirs(local_folder, exist_ok=True)
        ext = filename.split('.')[-1]
        return os.path.join('operators', 'licenses', 'front', f"{uuid.uuid4()}.{ext}")

def upload_operator_license_back(instance, filename):
    """Sube reverso de licencia a S3 o local"""
    if settings.USE_S3:
        return get_s3_file_path(instance, filename, 'operators/licenses/back')
    else:
        local_folder = os.path.join(settings.MEDIA_ROOT, 'operators', 'licenses', 'back')
        os.makedirs(local_folder, exist_ok=True)
        ext = filename.split('.')[-1]
        return os.path.join('operators', 'licenses', 'back', f"{uuid.uuid4()}.{ext}")

# =====================================================================
# Funciones para Órdenes (Order)
# =====================================================================
def upload_evidence_file(instance, filename):
    """Sube evidencias de órdenes"""
    if settings.USE_S3:
        return get_s3_file_path(instance, filename, 'orders/evidence')
    else:
        local_folder = os.path.join(settings.MEDIA_ROOT, 'evidences')
        os.makedirs(local_folder, exist_ok=True)
        ext = filename.split('.')[-1].lower()
        return os.path.join('evidences', f"{uuid.uuid4()}.{ext}")

def upload_dispatch_file(instance, filename):
    """Sube tickets de despacho"""
    if settings.USE_S3:
        return get_s3_file_path(instance, filename, 'orders/dispatch')
    else:
        local_folder = os.path.join(settings.MEDIA_ROOT, 'dispatch_tickets')
        os.makedirs(local_folder, exist_ok=True)
        ext = filename.split('.')[-1].lower()
        short_uuid = str(uuid.uuid4()).split('-')[0]
        return os.path.join('dispatch_tickets', f"{short_uuid}.{ext}")