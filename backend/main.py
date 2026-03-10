import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)