import os


class Config:
    def __init__(self):
        # Environment
        self.DD_ENV = os.environ.get('DD_ENV', 'localhost')
        self.DEBUG_UTILS = os.environ.get('DEBUG_UTILS', False)
        self.REPOSITORY = os.environ.get('REPOSITORY', 'msa_repository')
        self.TYPE_DEPLOY = os.environ.get('TYPE_DEPLOY', 'api')

        # AWS
        self.AWS_PROFILE_NAME = os.environ.get('AWS_PROFILE_NAME', 'default')
        self.AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')
        self.SECRET_NAME = os.environ.get('SECRET_NAME', 'api/testing/ms-communicator')

        # Opentelemtry
        self.OTLP_HOST = os.environ.get('OTLP_HOST', 'localhost')
        self.OTLP_PORT = os.environ.get('OTLP_PORT', '0000')
        self.OTLP_NAME = os.environ.get('OTLP_NAME', 'ms-localhost')

        # DataDog
        self.DD_HOST = os.environ.get('DD_HOST', 'localhost')
        self.DD_PORT = os.environ.get('DD_PORT', '8126')
