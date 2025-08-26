import os

import vtk


def vtk_polydata_writer(filename, data, store_binary=False, store_xml=False):
    """Writes a vtk polydata grid to specified filename this has to include the full path"""
    if not (filename.endswith('.vtk') or filename.endswith(".vtp")):
        raise ValueError(f'Filename must end with .vtk or .vtp but was {filename}')
    if store_xml:
        writer = vtk.vtkXMLPolyDataWriter()
    else:
        writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    if store_binary:
        writer.SetFileTypeToBinary()
    writer.Write()


def vtk_unstructured_grid_writer(filename, data, store_binary=False):
    if not (filename.endswith('.vtk') or filename.endswith(".vtu")):
        raise ValueError(f'Filename must end with .vtk or .vtu but was {filename}')
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    if store_binary:
        writer.SetFileTypeToBinary()
    writer.Write()


def vtk_xml_unstructured_grid_writer(filename, data):
    if not (filename.endswith('.vtk') or filename.endswith(".vtu")):
        raise ValueError(f'Filename must end with .vtk or .vtu but was {filename}')
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def vtk_obj_writer(filename, data):
    if not filename.endswith('.obj'):
        raise ValueError(f'Filename must end with .obj but was {filename}')
    writer = vtk.vtkOBJWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def write_to_vtx(filename, data, try_append=False):
    """
    Writes the data to a .vtx file
    :param filename: Filename to write the data to with .vtx extension
    :param data: The data to write. Can be a list/array or single values
    :param try_append: Set to true if you like to append to existing .vtx file
    :return:
    """
    if not filename.endswith('.vtx'):
        raise ValueError(f'Filename must end with .vtx but was {filename}')
    length_data = len(data) if hasattr(data, '__len__') else 1
    if try_append and os.path.exists(filename):
        f = open(filename, 'a')
    else:
        f = open(filename, 'w')
        f.write(f'{length_data}\n')
        f.write('extra\n')

    if hasattr(data, '__iter__') or hasattr(data, '__getitem__'):
        for i in data:
            f.write(f'{i}\n')
    else:
        f.write(f'{data}\n')
    f.close()
