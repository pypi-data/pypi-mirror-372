import boto3
import os
import logging
from typing import Optional
from fk_utils import SETTINGS

# Configuración del logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Crear clientes de Boto3 fuera de las funciones
ssm_client = boto3.client('ssm', region_name=SETTINGS.AWS_REGION_NAME)


def get_parameter(param: str, param_type: str) -> Optional[str]:
    """
    Obtiene un parámetro de AWS Systems Manager Parameter Store.

    Args:
        param (str): Nombre del parámetro.
        param_type (str): Tipo de parámetro (static, global, static_env, default).

    Returns:
        str: Valor del parámetro o 'None' si hay un error.
    """
    try:
        param_mappings = {
            'static': f"/ecs/{SETTINGS.REPOSITORY}_{SETTINGS.TYPE_DEPLOY}/{param}",
            'global': f"/ecs/global/{param}",
            'static_env': f"/ecs/{SETTINGS.DD_ENV}/{param}",
            'default': f"/ecs/{SETTINGS.DD_ENV}/{SETTINGS.REPOSITORY}_{SETTINGS.TYPE_DEPLOY}/{param}"
        }

        param_name = param_mappings.get(param_type, param_mappings['default'])

        response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f'Error al obtener el parámetro en AWS: {str(e)}')

    return os.environ.get(param, 'None')
