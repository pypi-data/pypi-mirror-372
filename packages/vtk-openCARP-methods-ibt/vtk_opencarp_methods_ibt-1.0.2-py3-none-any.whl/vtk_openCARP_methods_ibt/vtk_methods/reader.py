import os

import vtk


def smart_reader(path):
    """
       Reads in vtk, vtp, vtu, ply and obj files to corresponding mesh classes
       From AugmentA modified to be more robust
    :param path: Path to file with extension
    :return:
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exists")

    extension = str(path).split(".")[-1]

    if extension == "vtk":
        data_checker = vtk.vtkDataSetReader()
        data_checker.SetFileName(str(path))
        data_checker.Update()
        data_type_name = data_checker.GetOutput().GetClassName()

        if data_checker.IsFilePolyData():
            reader = vtk.vtkPolyDataReader()
        elif data_checker.IsFileUnstructuredGrid():
            reader = vtk.vtkUnstructuredGridReader()
        else:
            raise ValueError(f"Type not found or implemented. Was a {data_type_name} file")
        _turn_all_read_on(reader)

    elif extension == "vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif extension == "vtu":
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif extension == "obj":
        reader = vtk.vtkOBJReader()
    elif extension == "ply":
        reader = vtk.vtkPLYReader()
        _turn_all_read_on(reader)
    else:
        raise ValueError(f"Type not found or implemented. File {path} not readable")

    reader.SetFileName(str(path))
    reader.Update()
    output = reader.GetOutput()

    return output


def _turn_all_read_on(reader):
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.ReadAllTensorsOn()
    reader.ReadAllFieldsOn()
    return reader


def vtx_reader(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exists")

    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Skip the first line (number of elements)
        for line in lines[1:]:
            line = line.strip()
            if line.isdigit():
                data.append(int(line))
    return data
