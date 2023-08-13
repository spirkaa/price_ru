import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import price_ru.app as app  # noqa: F401 E402
