import sys
from pathlib import Path

# Allow running directly from a source checkout without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from arithmetic.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
