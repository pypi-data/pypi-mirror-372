import vtk

from ..vtk_methods import thresholding
from ..vtk_methods.filters import apply_vtk_geom_filter, clean_polydata
from ..vtk_methods.init_objects import init_connectivity_filter, ExtractionModes

vtk_version = vtk.vtkVersion.GetVTKSourceVersion().split()[-1].split('.')[0]




def extract_largest_region(mesh):
    connect = init_connectivity_filter(mesh, ExtractionModes.LARGEST_REGION)
    surface = apply_vtk_geom_filter(connect.GetOutput())

    return clean_polydata(surface)


from enum import IntEnum


class ThresholdMode(IntEnum):
    UPPER = 0
    LOWER = 1
    BETWEEN = 2


def vtk_thr(model, mode: ThresholdMode | int, points_cells, array, thr1, thr2="None"):
    """
    DEPRECATED use vtk_opencarp_helper_methods.vtk.thresholding instead
    
    Args:
        mode: ThresholdMode enum or int (0=UPPER, 1=LOWER, 2=BETWEEN)
    """
    if mode == ThresholdMode.UPPER:
        thresh = thresholding.get_upper_threshold(model, thr1, "vtkDataObject::FIELD_ASSOCIATION_" + points_cells,
                                                  array)

    elif mode == ThresholdMode.LOWER:
        thresh = thresholding.get_lower_threshold(model, thr1, "vtkDataObject::FIELD_ASSOCIATION_" + points_cells,
                                                  array)

    elif mode == ThresholdMode.BETWEEN:
        thresh = thresholding.get_threshold_between(model, thr1, thr2,
                                                    "vtkDataObject::FIELD_ASSOCIATION_" + points_cells,
                                                    array)
    else:
        raise ValueError("Invalid mode")
    output = thresh.GetOutput()

    return output
