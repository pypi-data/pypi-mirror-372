import vtk

from ..vtk_methods.converters import vtk_to_numpy


def find_closest_point(dataset, point):
    loc = vtk.vtkPointLocator()
    loc.SetDataSet(dataset)
    loc.BuildLocator()
    return loc.FindClosestPoint(point)


def get_global_cell_ids(mesh, id_array_name="Global_ids"):
    return get_cell_ids(mesh, id_array_name).astype(int)


def get_cell_ids(mesh, id_array_name):
    return vtk_to_numpy(mesh.GetCellData().GetArray(id_array_name))


def get_points(mesh):
    return vtk_to_numpy(mesh.GetPoints().GetData())
