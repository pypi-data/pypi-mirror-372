import boto3
import json
import logging
from typing import Optional
from fk_utils import SETTINGS

# Configuración del logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Crear clientes de Boto3 fuera de las funciones
secrets_manager_client = boto3.client('secretsmanager', region_name=SETTINGS.AWS_REGION_NAME)


def get_secret_key() -> Optional[dict]:
    """
    Obtiene la clave secreta almacenada en AWS Secrets Manager.

    Returns:
        dict or None: Diccionario con la clave secreta o None si hay un error.
    """
    try:
        response = secrets_manager_client.get_secret_value(SecretId=SETTINGS.SECRET_NAME)
        secret_value = response.get('SecretString')

        if secret_value:
            return json.loads(secret_value)
    except Exception as e:
        logger.error(f'Error al obtener el secreto: {str(e)}')

    return None
