import sys
from pathlib import Path

# Dynamically add the package directory to sys.path
package_path = str(Path(__file__).parent.absolute())
if package_path not in sys.path:
    sys.path.insert(0, package_path)
