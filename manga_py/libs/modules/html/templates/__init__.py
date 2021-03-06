# DO NOT EDIT THIS FILE!
from pathlib import Path
path = Path(Path(__file__).resolve().parent)  # current dir


def get_index() -> str:
    with open(path.joinpath('index.html', 'r')) as f:
        scripts = """
<script src="vue.min.js"></script>
<script src="router.min.js"></script>
<script src="script.js"></script>
        """
        return f.read().format(scripts)
