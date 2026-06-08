import os
from dotenv import load_dotenv
import logging

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
TEMP_DIR = os.getenv("TEMP_DIR", "/app/temp")

os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if not NVIDIA_API_KEY:
    logging.warning("NVIDIA_API_KEY не найден. Анализ изображений может не работать.")
if not REPLICATE_API_TOKEN:
    logging.warning("REPLICATE_API_TOKEN не найден. Генерация через Replicate будет недоступна.")