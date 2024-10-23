import logging
import sys


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
sys.stdout.reconfigure(encoding='utf-8')
logger = logging.getLogger(__name__)