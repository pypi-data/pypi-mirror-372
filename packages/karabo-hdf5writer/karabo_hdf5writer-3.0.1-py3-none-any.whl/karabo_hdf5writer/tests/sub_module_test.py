import pytest

from karabo.common.api import has_sub_imports
from karabo.middlelayer.testing import get_ast_objects

from .. import hdf5writer


@pytest.mark.xfail(
        reason="Require the middlelayer.proxybase.SubproxyBase import!")
def test_import_sub_modules():
    """Check the device package for forbidden subimports"""
    ignore = ["karabo.middlelayer.testing"]
    ast_objects = get_ast_objects(hdf5writer)
    for ast_obj in ast_objects:
        for mod in ["karabo.middlelayer", "karabo.middlelayer_api"]:
            assert not len(has_sub_imports(ast_obj, mod, ignore))
