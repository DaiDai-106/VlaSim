import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source"))

from source.vlasim.app.run_sim_server import main

if __name__ == "__main__":
    main()
