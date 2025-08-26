import numpy as np
import vtk

from .converters import vtk_to_numpy, numpy_to_vtk
from ..vtk_methods.filters import get_vtk_geom_filter_port, clean_polydata, get_cells_with_ids


def get_maximum_distance_of_points(points, point_center):
    """
    Returns the maximum distance to the point_center.
    :param points: Has to be a vtk object on which GetPoints() can be executed
    :param point_center:
    :return: the maximum distance between the point_center and the points
    """
    valve_pts = vtk_to_numpy(points.GetPoints().GetData())
    max_dist = 0
    for l in range(len(valve_pts)):
        if np.sqrt(np.sum((point_center - valve_pts[l]) ** 2, axis=0)) > max_dist:
            max_dist = np.sqrt(np.sum((point_center - valve_pts[l]) ** 2, axis=0))

    return max_dist


def cut_mesh_with_radius(mesh, valve_center, max_cutting_radius):
    el_to_del_tot = find_elements_within_radius(mesh, valve_center, max_cutting_radius)
    return cut_elements_from_mesh(mesh, el_to_del_tot)


def cut_elements_from_mesh(mesh, elem_to_delete):
    cell_id_all = list(range(mesh.GetNumberOfCells()))
    el_diff = list(set(cell_id_all).difference(elem_to_delete))

    geo_filter_port, geo_filter = get_vtk_geom_filter_port(get_cells_with_ids(mesh, el_diff))

    return clean_polydata(geo_filter_port, input_is_connection=True)


def find_elements_within_radius(mesh, points_data, radius):
    mesh_id_list = find_points_within_radius(mesh, points_data, radius)

    mesh_cell_id_list = vtk.vtkIdList()
    mesh_cell_temp_id_list = vtk.vtkIdList()
    for i in range(mesh_id_list.GetNumberOfIds()):
        mesh.GetPointCells(mesh_id_list.GetId(i), mesh_cell_temp_id_list)
        for j in range(mesh_cell_temp_id_list.GetNumberOfIds()):
            mesh_cell_id_list.InsertNextId(mesh_cell_temp_id_list.GetId(j))

    id_set = set()
    for i in range(mesh_cell_id_list.GetNumberOfIds()):
        id_set.add(mesh_cell_id_list.GetId(i))

    return id_set


def find_points_within_radius(mesh, center_point, radius):
    """
    Gets points within a radius around the center_point.
    :param mesh: Has to be a vtk mesh
    :param center_point: point in coordinates (x,y,z)
    :param radius: Radius in units of the mesh
    :return:
    """
    locator = vtk.vtkStaticPointLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    mesh_id_list = vtk.vtkIdList()
    locator.FindPointsWithinRadius(radius, center_point, mesh_id_list)
    return mesh_id_list


def add_vectors_to_vtk(mesh, vectors, name, is_cell_array=True):
    """
    Adds a set of vectors to a vtk object as a cell array with a given name.
    :param mesh: A vtk object.
    :param vectors: A numpy based array of vectors.
    :param name: The name of the resulting cell array
    :param is_cell_array: If True, the resulting array is added to cell data otherwise to point data.
    :return:
    """
    vtk_array = numpy_to_vtk(vectors, deep=True)
    vtk_array.SetName(name)
    if is_cell_array:
        mesh.GetCellData().AddArray(vtk_array)
    else:
        mesh.GetPointData().AddArray(vtk_array)
