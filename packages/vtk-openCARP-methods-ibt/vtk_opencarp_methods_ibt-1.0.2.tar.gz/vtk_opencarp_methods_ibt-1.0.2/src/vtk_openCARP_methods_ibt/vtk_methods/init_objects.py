import vtk
from enum import Enum

from ..mathematical_operations.vector_operations import get_normalized_cross_product


def initialize_plane(norm_1, center):
    plane = vtk.vtkPlane()
    plane.SetNormal(norm_1[0], norm_1[1], norm_1[2])
    plane.SetOrigin(center[0], center[1], center[2])
    return plane


def initialize_plane_with_points(norm_center_point, point_a, point_b, plane_origin, invert_norm=False):
    """
    Creates a plane for given vectors.
    Plane is defined by a perpendicular vector n and a center point (plane_origin)
    The perpendicular vector is the cross product between the norm_center_point and point_a and point_b.
    :param norm_center_point: Center for building the perpendicular vector
    :param point_a:
    :param point_b:
    :param plane_origin:
    :param invert_norm: Inverts the perpendicular vector of the plane
    :return:
    """

    norm_1 = get_normalized_cross_product(norm_center_point, point_a, point_b)
    if invert_norm:
        norm_1 = -norm_1

    return initialize_plane(norm_1, plane_origin)


class ExtractionModes(Enum):
    ALL_REGIONS = "all_regions"
    SPECIFIED_REGIONS = "specified_regions"
    LARGEST_REGION = "largest_region"
    CLOSEST_POINT = "closest_point"
    CLOSEST_POINT_REGION = "closest_point_region"


def init_connectivity_filter(input, extraction_mode: ExtractionModes, color_regions=False, closest_point=None):
    """
    Returns an initialized connectivity filter with update applied
    :param closest_point: Set closest point if the extraction mode is set to the closest point
    :param input: The inout data
    :param extraction_mode: One of the implemented connectivity modes. See class ConnectivityModes
    :param color_regions:
    :return:
    """
    connect = vtk.vtkConnectivityFilter()
    connect.SetInputData(input)
    if extraction_mode == ExtractionModes.ALL_REGIONS:
        connect.SetExtractionModeToAllRegions()
    elif extraction_mode == ExtractionModes.SPECIFIED_REGIONS:
        connect.SetExtractionModeToSpecifiedRegions()
    elif extraction_mode == ExtractionModes.LARGEST_REGION:
        connect.SetExtractionModeToLargestRegion()
    elif extraction_mode == ExtractionModes.CLOSEST_POINT:
        connect.SetExtractionModeToClosestPoint()
    elif extraction_mode == ExtractionModes.CLOSEST_POINT_REGION:
        connect.SetExtractionModeToClosestPointRegion()
    else:
        ValueError("Invalid extraction mode")

    if extraction_mode==ExtractionModes.CLOSEST_POINT or extraction_mode==ExtractionModes.CLOSEST_POINT_REGION:
        assert closest_point.any() is not None, "Closest point not set"
        connect.SetClosestPoint(closest_point)

    if color_regions:
        connect.ColorRegionsOn()
    connect.Update()
    return connect
