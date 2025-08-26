import vtk
from pyvista.core import grid

from src.vtk_openCARP_methods_ibt.openCARP.exporting import write_mesh_from_vtk_obj


def test_vtk_to_openCARP():
    """
    Test creating a VTK file and exporting to openCARP format
    """
    grid = _setup_basic_geom()
    _setup_fibers(grid)
    _setup_sheet(grid)
    _setup_elm_tag(grid)

    # Export to openCARP format
    write_mesh_from_vtk_obj("test_opencarp",grid)
    # Verify exported files exist and contain correct data
    with open("test_opencarp.pts", "r") as f:
        pts_content = f.readlines()
    assert len(pts_content) > 0

    with open("test_opencarp.lon", "r") as f:
        lon_content = f.readlines()
    assert len(lon_content) > 0
    assert "1.0000 0.0000 0.0000" in lon_content[1]

    with open("test_opencarp.elem", "r") as f:
        elem_content = f.readlines()
    assert len(elem_content) > 0
    assert "Tr" in elem_content[1]

def test_without_sheet():
    grid = _setup_basic_geom()
    _setup_fibers(grid)
    _setup_elm_tag(grid)

    write_mesh_from_vtk_obj("test_opencarp", grid)

    with open("test_opencarp.lon", "r") as f:
        lon_content = f.readlines()
    assert len(lon_content) > 0
    assert "1.0000 0.0000 0.0000" in lon_content[1]




def _setup_elm_tag(grid):
    # Add element tags
    elemTag = vtk.vtkIntArray()
    elemTag.SetName("elemTag")
    elemTag.SetNumberOfComponents(1)
    elemTag.SetNumberOfTuples(grid.GetNumberOfCells())
    for i in range(grid.GetNumberOfCells()):
        elemTag.SetValue(i, 1)
    grid.GetCellData().AddArray(elemTag)


def _setup_sheet(grid):
    sheet = vtk.vtkDoubleArray()
    sheet.SetNumberOfComponents(3)
    sheet.SetName("sheet")
    for i in range(grid.GetNumberOfCells()):
        sheet.InsertNextTuple3(0.0, 1.0, 0.0)
    grid.GetCellData().AddArray(sheet)


def _setup_fibers(grid):
    fibers = vtk.vtkDoubleArray()
    fibers.SetNumberOfComponents(3)
    fibers.SetName("fiber")
    for i in range(grid.GetNumberOfCells()):
        fibers.InsertNextTuple3(1.0, 0.0, 0.0)
    grid.GetCellData().AddArray(fibers)


def _setup_basic_geom():
    # Create VTK points
    points = vtk.vtkPoints()
    points.InsertNextPoint(0.0, 0.0, 0.0)
    points.InsertNextPoint(1.0, 0.0, 0.0)
    points.InsertNextPoint(0.0, 1.0, 0.0)
    # Create polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    # Create triangle
    triangle = vtk.vtkTriangle()
    triangle.GetPointIds().SetId(0, 0)
    triangle.GetPointIds().SetId(1, 1)
    triangle.GetPointIds().SetId(2, 2)
    # Add cell to grid
    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.InsertNextCell(triangle.GetCellType(), triangle.GetPointIds())
    return grid
