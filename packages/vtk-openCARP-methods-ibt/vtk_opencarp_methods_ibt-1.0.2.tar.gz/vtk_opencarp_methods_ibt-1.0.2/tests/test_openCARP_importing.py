import pytest

from ..src.vtk_openCARP_methods_ibt.vtk_methods.exporting import vtk_polydata_writer
from ..src.vtk_openCARP_methods_ibt.openCARP.importing import convert_openCARP_to_vtk


def test_working_conversion():
    test_file = "data/cube"
    resulting_mesh=convert_openCARP_to_vtk(test_file + ".pts", test_file + ".elem", test_file + ".lon")
    vtk_polydata_writer(test_file+".vtk", resulting_mesh)

def test_wrong_filename():
    test_file = "data/cube_wrong"
    with pytest.raises(FileNotFoundError):
        convert_openCARP_to_vtk(test_file + ".pts", test_file + ".elem", test_file + ".lon")

