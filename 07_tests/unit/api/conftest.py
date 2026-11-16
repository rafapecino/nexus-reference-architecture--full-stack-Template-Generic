import sys
from pathlib import Path

# Add 01_src/api to sys.path so that 'interfaces', 'application', 'domain' etc. are importable
sys.path.insert(0, str(Path(__file__).parents[3] / "01_src" / "api"))
