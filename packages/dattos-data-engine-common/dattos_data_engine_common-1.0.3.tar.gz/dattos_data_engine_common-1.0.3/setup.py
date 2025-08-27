import setuptools
import os
import re


def get_version():
    init_path = os.path.join(
        os.path.dirname(__file__), "src", "dattos_data_engine_common", "__init__.py"
    )
    with open(init_path, encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not match:
        raise RuntimeError("Cannot find __version__ in __init__.py")
    return match.group(1)


setuptools.setup(
    version=get_version(),
)
