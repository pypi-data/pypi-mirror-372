global center
import numpy as np
import pyvista as pv
import vtk


def are_normals_outside(mesh):
    """
    Determine if the normals of the mesh point outside the center of the mesh.
    Based on stochastic evaluation of 100 points to be able to process large meshes fast.
    :param mesh: A vtk mesh object
    :return: True if the normals of the mesh point outside, false otherwise
    """
    mesh_with_normals = generate_normals(mesh)

    pv_mesh = pv.wrap(mesh_with_normals)
    points = pv_mesh.points
    normals = pv_mesh.point_data['Normals']

    sample_normals, sample_points = get_sampled_points_and_normals(normals, points)

    mesh_center = points.mean(axis=0)
    vectors_center_to_points = sample_points - mesh_center
    dot_products = np.sum(sample_normals * vectors_center_to_points, axis=1)
    if np.mean(dot_products) < 0:
        print("Normals point inward.")
        return False
    else:
        print("Normals point outward.")
        return True


def get_sampled_points_and_normals(normals, points, number_of_samples=1000):
    """
    Get a random subset of points and normals.
    :param normals: Array of all normals as n-dimensional array
    :param points: Array of all points as n-dimensional array
    :param number_of_samples: How many points/normals should be sampled
    :return:
    """
    num_points = points.shape[0]
    sample_indices = np.random.choice(num_points, min(number_of_samples, num_points), replace=False)
    sample_points = points[sample_indices]
    sample_normals = normals[sample_indices]
    return sample_normals, sample_points


def generate_normals(mesh):
    """
    Generates the normals for a given vtk polydata mesh
    :param mesh: Polydata mesh with normals as array
    :return:
    """
    normal_generator = vtk.vtkPolyDataNormals()
    normal_generator.SetInputData(mesh)
    normal_generator.ComputePointNormalsOn()
    normal_generator.ComputeCellNormalsOff()
    normal_generator.Update()
    polydata_with_normals = normal_generator.GetOutput()
    return polydata_with_normals
