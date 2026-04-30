BASE_URL = "https://www.diabolik.it"
ALBO_URL = f"{BASE_URL}/albo"

START_SLUG = "Il-re-del-terrore"

SLEEP_MIN = 1.0
SLEEP_MAX = 2.0

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BACKOFF = 2

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

DB_PATH = "diabolik.db"
COVERS_DIR = "covers"

NON_INEDITO_KEYWORDS = [
    "Fuori Serie",
    "GRANDE DIABOLIK",
    "MAGNUM",
    "DK",
]

TEST_LIMIT = 5
