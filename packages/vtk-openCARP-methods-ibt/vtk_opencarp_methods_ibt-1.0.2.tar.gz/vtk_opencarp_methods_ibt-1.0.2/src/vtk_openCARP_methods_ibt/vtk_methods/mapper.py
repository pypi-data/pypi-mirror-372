from pathlib import Path

import numpy as np
import vtk
from scipy.spatial import KDTree
from vtkmodules.numpy_interface import dataset_adapter as dsa

from ..openCARP.exporting import write_to_pts
from ..vtk_methods.converters import vtk_to_numpy
from ..vtk_methods.exporting import vtk_unstructured_grid_writer, write_to_vtx
from ..vtk_methods.reader import vtx_reader, smart_reader


def point_array_mapper(mesh1, mesh2, idat):
    """

    :param mesh1:
    :param mesh2:
    :param idat: Set to "all" to mapp all arrays, else choose a specific array
    :return: Mapped mesh
    """
    pts1 = vtk_to_numpy(mesh1.GetPoints().GetData())
    pts2 = vtk_to_numpy(mesh2.GetPoints().GetData())

    meshNew = _point_array_mapper(idat, mesh1, mesh2, pts1, pts2)

    return meshNew.VTKObject


def _point_array_mapper(idat, mesh1, mesh2, pts1, pts2):
    """

    :param idat: Set to "all" to mapp all arrays, else choose a specific array
    :param mesh1:
    :param mesh2:
    :param pts1:
    :param pts2:
    :return:
    """
    tree = KDTree(pts1)
    dd, ii = tree.query(pts2, workers=-1)
    meshNew = dsa.WrapDataObject(mesh2)
    if idat == "all":
        for i in range(mesh1.GetPointData().GetNumberOfArrays()):
            data = vtk_to_numpy(
                mesh1.GetPointData().GetArray(mesh1.GetPointData().GetArrayName(i)))
            data2 = data[ii]
            data2 = np.where(np.isnan(data2), 10000, data2)

            meshNew.PointData.append(data2, mesh1.GetPointData().GetArrayName(i))
    else:
        data = vtk_to_numpy(mesh1.GetPointData().GetArray(idat))
        data2 = data[ii]
        meshNew.PointData.append(data2, idat)
    return meshNew


def cell_array_mapper(mesh1, mesh2, mesh2_name, idat):
    """

    :param mesh1: Vtk mesh object
    :param mesh2: Vtk mesh object
    :param mesh2_name:
    :param idat: Set to "all" to mapp all arrays, else choose a specific array
    :return: Returns mesh and also stores it to disk with subfix "_with_data"
    """
    filter_cell_centers = vtk.vtkCellCenters()
    filter_cell_centers.SetInputData(mesh1)
    filter_cell_centers.Update()
    centroids1 = filter_cell_centers.GetOutput().GetPoints()
    centroids1_array = vtk_to_numpy(centroids1.GetData())

    filter_cell_centers = vtk.vtkCellCenters()
    filter_cell_centers.SetInputData(mesh2)
    filter_cell_centers.Update()
    centroids2 = filter_cell_centers.GetOutput().GetPoints()
    pts2 = vtk_to_numpy(centroids2.GetData())

    meshNew = _cell_array_mapper(idat, mesh1, mesh2, centroids1_array, pts2)

    vtk_unstructured_grid_writer(f"{mesh2_name.split('.')[0]}_with_data.vtk", meshNew.VTKObject)

    return meshNew.VTKObject


def _cell_array_mapper(idat, mesh1, mesh2, array1, array2):
    """

    :param idat: Set to "all" to mapp all arrays, else choose a specific array
    :param mesh1:
    :param mesh2:
    :param array1:
    :param array2:
    :return:
    """
    tree = KDTree(array1)
    dd, ii = tree.query(array2, workers=-1)
    meshNew = dsa.WrapDataObject(mesh2)
    if idat == "all":
        for i in range(mesh1.GetCellData().GetNumberOfArrays()):
            data = vtk_to_numpy(
                mesh1.GetCellData().GetArray(mesh1.GetCellData().GetArrayName(i)))
            data2 = data[ii]
            meshNew.CellData.append(data2, mesh1.GetCellData().GetArrayName(i))
    else:
        data = vtk_to_numpy(mesh1.GetCellData().GetArray(idat))
        data2 = data[ii]
        meshNew.CellData.append(data2, idat)
    return meshNew


def mapp_ids_for_folder(source_folder, dest_folder, source_mesh, dest_mesh, debug=False):
    """
    Maps all vtx files from one folder to another folder with two different meshes as a base.
    vtx files in source folder has to be originated from the source mesh.
    All the vtx files in the dest_folder will be in correspondence to the dest_mesh
    :param debug: If true all the vtx files will also be stored as .pts file for better inspection
    :param source_folder:Path to a folder with vtx files
    :param dest_folder: Path to a folder where the results are stored
    :param source_mesh: original vtk mesh
    :param dest_mesh: mesh for the reference of the newly generated points
    :return:
    """
    num_converted_files = 0
    folder = Path(source_folder)
    for file in folder.glob("ids_*.vtx"):
        if file.is_file():  # Ensure it's a file
            print(f"Processing file: {file.name}")
            # Read the content of the .vtx file
            vtx_data = vtx_reader(file)
            remapped_ids = remap_ids(source_mesh, dest_mesh, vtx_data)
            write_to_vtx(f"{dest_folder}/{file.name}", remapped_ids)
            num_converted_files += 1
            if debug:
                write_to_pts(f"{dest_folder}/{file.name}.pts",
                             [dest_mesh.GetPoint(closest_id) for closest_id in remapped_ids]
                             )
    print(f"Number of converted files: {num_converted_files}")


def remap_ids(source_mesh, dest_mesh, source_point_ids):
    """
    Maps source point_id_s coming from the source_mesh to ids from the dest_mesh.
    :param source_mesh: vtk mesh
    :param dest_mesh: vtk mesh
    :param source_point_ids: array
    :return: Array with the new ids
    """
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(dest_mesh)
    locator.BuildLocator()

    new_ids = []
    for source_id in source_point_ids:
        point = source_mesh.GetPoint(source_id)
        closest_id = locator.FindClosestPoint(point)
        new_ids.append(closest_id)

    return new_ids


def ids_to_pts(ids, mesh):
    """
    Converts ids to pts which can be exported to a pts file
    :param ids: The point ids for the mesh
    :param mesh:
    :return:
    """
    points = []
    for id in ids:
        points.append(mesh.GetPoint(id))
    return points


def vtx_to_pts(vtx_filename, pts_filename, mesh_filename):
    ids = vtx_reader(vtx_filename)
    mesh = smart_reader(mesh_filename)
    points = ids_to_pts(ids, mesh)
    write_to_pts(pts_filename, points)
