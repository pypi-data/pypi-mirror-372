from vtkmodules.vtkCommonDataModel import vtkDataSet
from ..vtk_methods.converters import vtk_to_numpy
from ..vtk_methods.finder import get_cell_ids


def write_to_elem(filename, mesh, tag):
    """

    :param filename: Filename with .elem extension
    :param mesh: Mesh which should be stored as element file.
    :param tag: Tags which are attached to the mesh
    :return:
    """
    if not filename.endswith('.elem'):
        raise ValueError(f'Filename must end with .elem extension but was {filename}')
    with open(filename, "w") as f:
        f.write(f"{mesh.GetNumberOfCells()}\n")
        for i in range(mesh.GetNumberOfCells()):
            cell = mesh.GetCell(i)
            if cell.GetNumberOfPoints() == 2:
                f.write(
                    f"Ln {cell.GetPointIds().GetId(0)} {cell.GetPointIds().GetId(1)} {tag[i]}\n")
            elif cell.GetNumberOfPoints() == 3:
                f.write("Tr {} {} {} {}\n".format(cell.GetPointIds().GetId(0), cell.GetPointIds().GetId(1),
                                                  cell.GetPointIds().GetId(2), tag[i]))
            elif cell.GetNumberOfPoints() == 4:
                f.write("Tt {} {} {} {} {}\n".format(cell.GetPointIds().GetId(0), cell.GetPointIds().GetId(1),
                                                     cell.GetPointIds().GetId(2), cell.GetPointIds().GetId(3),
                                                     tag[i]))
            else:
                print("strange " + str(cell.GetNumberOfPoints()))


def write_to_lon(filename_lon, elem, sheet=None, precession=4):
    if not filename_lon.endswith('.lon'):
        raise ValueError(f'Filename must end with .lon extension but was {filename_lon}')

    if sheet is None:
        rows = (format_vector_to_str(e, precession) + "\n" for e in elem)
    else:
        rows = (format_vector_to_str(e, precession) + " " + format_vector_to_str(s, precession) + "\n"
                for e, s in zip(elem, sheet))
    with open(filename_lon, "w") as f:
        f.write("2\n")
        f.writelines(rows)


def format_vector_to_str(v, precision):
    return " ".join(f"{x:.{precision}f}" for x in v)


def write_to_pts(filename_pts, pts):
    if not filename_pts.endswith('.pts'):
        raise ValueError(f'Filename must end with .pts extension but was {filename_pts}')
    with open(filename_pts, "w") as f:
        f.write(f"{len(pts)}\n")
        for i in range(len(pts)):
            f.write(f"{pts[i][0]} {pts[i][1]} {pts[i][2]}\n")


def write_mesh(filename, pts, mesh: vtkDataSet, elem_tags, fiber_long=None, fiber_sheet=None):
    write_to_pts(filename + ".pts", pts)
    write_to_elem(filename + ".elem", mesh, elem_tags)
    if fiber_long is not None:
        write_to_lon(filename + ".lon", fiber_long, fiber_sheet)


def write_mesh_from_vtk_obj(filename: str, mesh, tag_name="elemTag", fiber_name="fiber", sheet_name="sheet"):
    pts = vtk_to_numpy(mesh.GetPoints().GetData())
    fibers = get_cell_ids(mesh, fiber_name)
    if mesh.GetCellData().HasArray(sheet_name):
        sheet = get_cell_ids(mesh, sheet_name)
    else:
        sheet = None
    tags = get_cell_ids(mesh, tag_name)
    write_mesh(filename, pts, mesh, tags, fibers, sheet)
