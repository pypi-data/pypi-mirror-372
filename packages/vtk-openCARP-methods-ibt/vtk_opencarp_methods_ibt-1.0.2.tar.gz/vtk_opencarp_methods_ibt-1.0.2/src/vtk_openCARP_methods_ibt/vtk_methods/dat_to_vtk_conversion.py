import argparse

import numpy as np
import vtk

from ..openCARP.importing import convert_openCARP_to_vtk
from ..vtk_methods.exporting import vtk_polydata_writer


def get_arguments():
    parser = argparse.ArgumentParser(description="Add data from a .dat file as PointData to a VTK mesh.")
    parser.add_argument("--dat_file", type=str, help="Path to the .dat file containing data.")
    parser.add_argument("--mesh_file", type=str, help="Path to the input VTK mesh file.")
    parser.add_argument("--array_name", type=str, help="Name of the data array in the target output mesh.")
    parser.add_argument("--output_file", type=str, help="Path to save the updated VTK mesh.")
    args = parser.parse_args()
    return args


def add_dat_to_openCARP_mesh(dat_file, openCARP_mesh_file, array_name, output_file):
    """
    Adds data from a .dat file as PointData to a openCARP .pts, .elem mesh.

    :param dat_file: Path to the .dat file containing data to add.
    :param openCARP_mesh_file: Path to the input openCARP file e.g Test-> Test.pts and Test.elem has to exist.
    :param array_name: Name of the array which is represented in the .dat file.
    :param output_file: Path to save the updated VTK mesh.
    """
    mesh = convert_openCARP_to_vtk(openCARP_mesh_file + ".pts", openCARP_mesh_file + ".elem")
    add_dat_to_vtk_mesh(dat_file, mesh, array_name, output_file)


def add_dat_to_vtk_mesh(dat_file, mesh, array_name, output_file, offset=0):
    """
    Adds data from a .dat file as PointData to a VTK mesh.
    :param dat_file: Path to the .dat file containing data to add.
    :param mesh: A VTKMesh in the .vtk format
    :param array_name: Name of the array which is represented in the .dat file.
    :param output_file: Path to save the updated VTK mesh.
    :param offset: Offset which is added to the data array.
    :return:
    """
    try:
        data = np.loadtxt(dat_file)
    except Exception as e:
        raise ValueError(f"Error loading .dat file: {e}")
    if mesh.GetNumberOfPoints() != data.size:
        raise ValueError(f"The number of points in the mesh ({mesh.GetNumberOfPoints()}) "
                         f"does not match the size of the data ({data.size}).")
    vtk_array = vtk.vtkFloatArray()
    vtk_array.SetName(array_name)
    vtk_array.SetNumberOfComponents(1)
    vtk_array.SetNumberOfTuples(data.size)
    for i, value in enumerate(data):
        vtk_array.SetValue(i, value + offset)
    mesh.GetPointData().AddArray(vtk_array)
    mesh.GetPointData().SetActiveScalars(array_name)
    vtk_polydata_writer(output_file, mesh)
    print(f"Updated VTK mesh written to: {output_file}")


if __name__ == "__main__":
    args = get_arguments()
    add_dat_to_openCARP_mesh(args.dat_file, args.mesh_file, args.array_name, args.output_file)
