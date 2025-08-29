# Logger configuration
import logging
import os

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s %(name)-32s %(levelname)-8s %(message)s')
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

payment_logger = logging.getLogger('oc-python-sdk.payment')
application_logger = logging.getLogger('oc-python-sdk.application')
