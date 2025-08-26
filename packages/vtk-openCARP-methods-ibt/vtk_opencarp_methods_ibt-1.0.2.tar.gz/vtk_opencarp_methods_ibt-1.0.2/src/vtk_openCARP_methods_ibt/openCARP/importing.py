import argparse
import os

import numpy as np
import vtk

from ..vtk_methods.helper_methods import add_vectors_to_vtk
from ..vtk_methods.exporting import vtk_polydata_writer


def load_pts(pts_file):
    """
    Loads a .pts file and converts it to an vtkPoints array
    The file is expected to start with the number of points, then lists the point coordinates.
    :param pts_file: the .pts file name with extension .pts
    :return: vtkPoints array
    """
    if not os.path.isfile(pts_file):
        raise FileNotFoundError(f"The .pts file {pts_file} does not exist!")
    if not pts_file.endswith(".pts"):
        raise ValueError(f"The .pts file {pts_file} is not a .pts file!")

    vtk_points = vtk.vtkPoints()
    pts_data = np.loadtxt(pts_file, skiprows=1, usecols=(0, 1, 2))
    num_points = int(np.loadtxt(pts_file, max_rows=1))

    if pts_data.shape[0] != num_points:
        raise ValueError("The number of points declared is not equal to the number of points in the .pts file!")

    for point in pts_data:
        vtk_points.InsertNextPoint(point)
    return vtk_points


def load_elem(elem_file_path):
    """
    Converts a .elem file into a vtkCellArray which is returned
    :param elem_file_path: Element file path with .elem extension
    :return:
    """
    if not os.path.isfile(elem_file_path):
        raise FileNotFoundError(f"The .elem file {elem_file_path} does not exist!")
    if not elem_file_path.endswith(".elem"):
        raise ValueError(f"The .elem file {elem_file_path} is not a .elem file!")

    with open(elem_file_path, 'r') as f:
        lines = f.readlines()

    num_elements = int(lines[0])
    vtk_cells = vtk.vtkCellArray()

    element_tags = []
    for line in lines[1:]:
        parts = line.split()
        num_pts_per_cell = len(parts) - 2

        cell = vtk.vtkIdList()
        for i in range(1, num_pts_per_cell + 1):
            cell.InsertNextId(int(parts[i]))
        vtk_cells.InsertNextCell(cell)
        element_tags.append(int(parts[-1]))

    if vtk_cells.GetNumberOfCells() != num_elements:
        raise ValueError("The number of elements declared is not equal to the number of elements in the .elem file!")
    return vtk_cells, element_tags


def load_lon(lon_file_path):
    if not os.path.exists(lon_file_path):
        raise FileNotFoundError(f"The file {lon_file_path} does not exist")
    with open(lon_file_path, "r") as file:
        lines = file.readlines()

    num_arrays = int(lines[0].strip())
    data = np.loadtxt(lines[1:])

    if num_arrays == 1:
        fibers = data.reshape(-1, 3)
        sheets = None
    elif num_arrays == 2:
        fibers = data[:, :3]
        sheets = data[:, 3:]
    else:
        raise ValueError("Invalid .lon file: must have 1 or 2 vector arrays.")

    return fibers, sheets


def convert_openCARP_to_vtk(pts_file_path, elem_file_path, lon_file_path=""):
    """
    Convert a .pts and .elem file to a .vtk file.
    :param pts_file_path: Filepath of the .pts file with .pts extension
    :param elem_file_path: Filepath of the .elem file with .elem extension
    :param lon_file_path: Filepath of the .lon file with .lon extension. Optional.
    :return: vtk polydata object
    """
    vtk_points = load_pts(pts_file_path)
    vtk_cells, element_tags = load_elem(elem_file_path)

    mesh = vtk.vtkPolyData()
    mesh.SetPoints(vtk_points)
    mesh.SetPolys(vtk_cells)

    cell_data_array = vtk.vtkIntArray()
    cell_data_array.SetName("elemTag")

    for cell_data in element_tags:
        cell_data_array.InsertNextValue(cell_data)

    mesh.GetCellData().SetScalars(cell_data_array)
    if lon_file_path:
        fibers, sheet = load_lon(lon_file_path)
        add_vectors_to_vtk(mesh, fibers, "fiber")
        if sheet is not None:
            add_vectors_to_vtk(mesh, sheet, "sheet")
    return mesh


def parse_args():
    parser = argparse.ArgumentParser(description="Convert openCARP mesh files to VTK format.")

    # Arguments with -- for flexible naming
    parser.add_argument('--pts-file', type=str, required=True, default="data/cube.pte",
                        help="Path to the .pts file containing node positions")
    parser.add_argument('--elem-file', type=str, required=True, default="data/cube.elem",
                        help="Path to the .elem file containing element connectivity")
    parser.add_argument('--lon-file', type=str, required=True, default="data/cube.lon",
                        help="Path to the .lon file containing fiber (and sheet direction)")
    parser.add_argument('--output-file', type=str, required=True, help="Path for the output VTK file")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    vtk_mesh = convert_openCARP_to_vtk(args.pts_file, args.elem_file)
    vtk_polydata_writer(args.output_file, vtk_mesh)
