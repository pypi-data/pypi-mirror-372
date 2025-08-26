import vtk

vtk_version = vtk.vtkVersion.GetVTKSourceVersion().split()[-1].split('.')[0]


def apply_vtk_geom_filter(geom, input_is_connection=False):
    geo_filter = vtk.vtkGeometryFilter()
    if input_is_connection:
        geo_filter.SetInputConnection(geom)
    else:
        geo_filter.SetInputData(geom)
    geo_filter.Update()
    return geo_filter.GetOutput()


def get_vtk_geom_filter_port(geom, input_is_connection=False):
    """
    Initializes an vtkGeometryFilter and returns the filter and the output port.
    Filter has to be returned otherwise it will be destroyed by the garbage collector
    :param geom: Input data or connection
    :param input_is_connection: True is the input is also an output port
    :return: the output port of the geometry filter and the geometry filter itself
    """
    geo_filter = vtk.vtkGeometryFilter()
    if input_is_connection:
        geo_filter.SetInputConnection(geom)
    else:
        geo_filter.SetInputData(geom)
    geo_filter.Update()
    return geo_filter.GetOutputPort(), geo_filter


def get_equidistant_points(mesh, tolerance=1.0, point_merging_on=True, tolerance_on=True):
    """
    Returns equidistant points with elements for given interpoint distance
    :param tolerance_on: Set to true, if a specific tolerance is to be applied
    :param mesh: Mesh on which the filter is to be applied
    :param tolerance: Tolerance given in mm
    :param point_merging_on: Enable point merging of vtk clean filter
    :return:
    """
    poly_mesh = apply_vtk_geom_filter(mesh)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(poly_mesh)
    if tolerance_on:
        clean.SetAbsoluteTolerance(tolerance)
        clean.ToleranceIsAbsoluteOn()
    if point_merging_on:
        clean.PointMergingOn()
    clean.Update()
    return clean.GetOutput()


def clean_polydata(input, input_is_connection=False):
    """
    Encapsulates the vtkCleanPolyData function
    :param input: Either the input mesh or a vtk input connection port
    :param input_is_connection: True if the input is an output port
    :return: applied clean polydata filter
    """
    cln = vtk.vtkCleanPolyData()
    if input_is_connection:
        cln.SetInputConnection(input)
    else:
        cln.SetInputData(input)
    cln.Update()
    return cln.GetOutput()


def vtk_append(geometries, merge_points=False):
    """
    Appends the geometries to one mesh
    :param geometries: List of at least 1 vtk meshes. Supports vtkPolyData and vtkUnstructuredGrid.
    Hast to be the same type for all the geometries. Has to be a list.
    :param merge_points: Set merge points flag of the append filter on or off.
    :return:
    """
    if len(geometries) < 1:
        raise ValueError("Append filter needs at least 1 input meshe")
    append_filter = vtk.vtkAppendFilter()

    for geom in geometries:
        append_filter.AddInputData(geom)

    append_filter.SetMergePoints(merge_points)
    append_filter.Update()
    return append_filter.GetOutput()


def generate_ids(mesh, point_ids_name, cell_ids_name, field_data_on=False):
    cell_id = vtk.vtkIdFilter()
    cell_id.CellIdsOn()
    cell_id.SetInputData(mesh)
    cell_id.PointIdsOn()
    if field_data_on:
        cell_id.FieldDataOn()
    if int(vtk_version) >= 9:
        cell_id.SetPointIdsArrayName(point_ids_name)
        cell_id.SetCellIdsArrayName(cell_ids_name)
    else:
        cell_id.SetIdsArrayName(point_ids_name)

    cell_id.Update()

    return cell_id.GetOutput()


def get_cells_with_ids(mesh, ids):
    id_list = vtk.vtkIdList()
    for var in ids:
        id_list.InsertNextId(var)

    return apply_extract_cell_filter(mesh, id_list)


def apply_extract_cell_filter(input, id_list, input_is_connection=False):
    """
    Extract cells from mesh based on the id_list
    :param input_is_connection: Set to true if the input is an output port
    :param input: Input mesh or connection
    :param id_list:
    :return:
    """
    extract = vtk.vtkExtractCells()
    if input_is_connection:
        extract.SetInputConnection(input)
    else:
        extract.SetInputData(input)
    extract.SetCellList(id_list)
    extract.Update()

    return extract.GetOutput()


def get_center_of_mass(mesh, set_use_scalars_as_weights):
    center_of_mass_filter = vtk.vtkCenterOfMass()
    center_of_mass_filter.SetInputData(mesh)
    center_of_mass_filter.SetUseScalarsAsWeights(set_use_scalars_as_weights)
    center_of_mass_filter.Update()
    return center_of_mass_filter.GetCenter()


def get_feature_edges(input_data, boundary_edges_on, feature_edges_on, manifold_edges_on, non_manifold_edges_on):
    feature_edge_filter = vtk.vtkFeatureEdges()
    feature_edge_filter.SetInputData(input_data)
    if boundary_edges_on:
        feature_edge_filter.BoundaryEdgesOn()
    else:
        feature_edge_filter.BoundaryEdgesOff()
    if feature_edges_on:
        feature_edge_filter.FeatureEdgesOn()
    else:
        feature_edge_filter.FeatureEdgesOff()
    if manifold_edges_on:
        feature_edge_filter.ManifoldEdgesOn()
    else:
        feature_edge_filter.ManifoldEdgesOff()
    if non_manifold_edges_on:
        feature_edge_filter.NonManifoldEdgesOn()
    else:
        feature_edge_filter.NonManifoldEdgesOff()

    feature_edge_filter.Update()
    return feature_edge_filter.GetOutput()


def get_elements_above_plane(input, plane, extract_boundary_cells_on=False, input_is_connection=False):
    """
    Encapsulates the vtkExtractGeometry filter and returns elements which lay above the specified plane.
    :param input_is_connection: Set to true if the input is an output port
    :param input: Input data or connection. Set input_is_connection to true if the input is an output port
    :param plane: vtkPlane
    :param extract_boundary_cells_on: True if the option to extract boundary cells should be turned on
    :return:
    """
    mesh_extract_filter = vtk.vtkExtractGeometry()
    if input_is_connection:
        mesh_extract_filter.SetInputConnection(input)
    else:
        mesh_extract_filter.SetInputData(input)
    mesh_extract_filter.SetImplicitFunction(plane)
    if extract_boundary_cells_on:
        mesh_extract_filter.ExtractBoundaryCellsOn()
    mesh_extract_filter.Update()
    return mesh_extract_filter.GetOutput()


def get_mesh_extract_filter_output(input_data, plane):
    return get_elements_above_plane(input_data, plane)


def translate_poly_data(mesh, translation):
    """
    Translates a polydata based on a three-dimensional translation vector
    :param mesh: VTK polydata mesh
    :param translation: Array with three indices for translation in x,y and z.
    :return:
    """
    if len(translation) != 3:
        raise ValueError(f"Translation must be a three dimensional array but was {len(translation)}")
    transform = vtk.vtkTransform()
    transform.Translate(translation[0], translation[1], translation[2])

    return apply_transform_filter(mesh, transform)


def apply_transform_filter(mesh, transform):
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(mesh)
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    return transform_filter.GetOutput()


def scale_poly_data(mesh, scale_factor):
    """
    Scales a polydata based on a scale factor
    :param mesh: VTK polydata mesh
    :param scale_factor: Factor which scales the mesh

    :return:
    """
    transform = vtk.vtkTransform()
    transform.Scale(scale_factor, scale_factor, scale_factor)
    return apply_transform_filter(mesh, transform)
