"""
Utilitaire de stockage de fichiers.
- Si CLOUDINARY_URL est défini dans l'env → upload vers Cloudinary (persistant)
- Sinon → stockage local dans /static/uploads/ (ephémère sur Railway)
"""
import os


def upload_file(local_path, public_id=None, resource_type='auto'):
    """
    Upload un fichier vers Cloudinary si configuré, sinon retourne None.
    Retourne le secure_url Cloudinary, ou None si pas configuré / erreur.
    """
    if not os.getenv('CLOUDINARY_URL'):
        return None
    try:
        import cloudinary
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            local_path,
            public_id=public_id,
            resource_type=resource_type,
            overwrite=True,
        )
        return result.get('secure_url')
    except Exception as e:
        print(f'[storage] Cloudinary upload error: {e}')
        return None


def is_cloud_configured():
    return bool(os.getenv('CLOUDINARY_URL'))
