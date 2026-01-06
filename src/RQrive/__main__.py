import sys

from pathlib import Path

module_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(module_root))


import RQrive

if __name__ == "__main__":
    RQrive.main()
