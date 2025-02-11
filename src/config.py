from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")


DATA_DIR = PROJ_ROOT / 'data'
DOCUMENTS_DIR = DATA_DIR / 'documentation/rust'
RAG_FILE = DOCUMENTS_DIR / 'doc.md'
TEST_DIR = PROJ_ROOT / 'tests'
