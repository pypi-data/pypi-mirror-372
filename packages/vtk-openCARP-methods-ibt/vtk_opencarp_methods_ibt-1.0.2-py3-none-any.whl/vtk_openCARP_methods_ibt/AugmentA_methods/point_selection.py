import pyvista as pv


def pick_point_with_preselection(mesh, object_str, current_point, point_scale=1):
    """
    Pick a point on a mesh interactively and select an orientation point
    :param mesh: The mesh where a point should be picked
    :param object_str: The name of the object which should be picked
    :param current_point: The current guess where the point is. Will be visualized.
    :param point_scale: Scale of the current point on the model
    :return:
    """
    p = pv.Plotter(notebook=False)
    if current_point is not None:
        point_cloud = pv.PolyData(current_point)
        p.add_mesh(point_cloud, color='w', point_size=30. * point_scale, render_points_as_spheres=True)
    p.add_mesh(mesh, color='r')
    p.enable_point_picking(mesh, use_picker=True)
    p.add_text(f'Select the {object_str} and close the window', position='lower_left')
    p.show()
    if p.picked_point is not None:
        current_point = p.picked_point
    elif current_point is not None:
        return current_point
    else:
        raise ValueError(f"Please select the {object_str}")
    return current_point


def pick_point(mesh, object_str):
    """
    Pick a point on a mesh interactively
    :param mesh: The mesh where a point should be picked
    :param object_str: The name of the object which should be picked
    :return:
    """
    return pick_point_with_preselection(mesh, object_str, None)
