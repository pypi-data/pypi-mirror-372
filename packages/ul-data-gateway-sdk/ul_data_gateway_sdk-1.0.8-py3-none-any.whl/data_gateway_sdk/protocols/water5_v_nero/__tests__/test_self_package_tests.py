import importlib
import os.path
from glob import glob

CWD = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../', '../', '../'))
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
MDL_PREF = os.path.relpath(PARENT_DIR, CWD).replace('/', '.').strip('.')


def test_some() -> None:
    for fn in glob(os.path.join(PARENT_DIR, '*.py')):
        if not os.path.isfile(fn) or '__' in fn:
            continue
        try:
            mdl = importlib.import_module(f'{MDL_PREF}.{os.path.basename(fn)[:-3]}')
        except Exception:  # noqa: B902
            continue
        for el in dir(mdl):
            if not el.startswith('test_'):
                continue
            getattr(mdl, el)()  # run test functions from each pack
    assert True
