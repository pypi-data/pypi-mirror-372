import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy as orig_vtk_numpy
from vtkmodules.util.numpy_support import numpy_to_vtk as orig_numpy_vtk

def vtk_to_numpy(vtk_data):
    return orig_vtk_numpy(vtk_data)


def numpy_to_vtk(numpy_data, deep=0, array_type=None):
    return orig_numpy_vtk(numpy_data, deep=deep, array_type=array_type)


def convert_point_to_cell_data(model, point_array_names=None):
    """
    Converts point wise data to cell data
    """

    pt_cell = vtk.vtkPointDataToCellData()
    pt_cell.SetInputData(model)
    if point_array_names is not None:
        pt_cell.CategoricalDataOff()
        pt_cell.ProcessAllArraysOff()
        for array_names in point_array_names:
            pt_cell.AddPointDataArray(array_names)
    pt_cell.PassPointDataOn()

    pt_cell.Update()

    return pt_cell.GetOutput()
