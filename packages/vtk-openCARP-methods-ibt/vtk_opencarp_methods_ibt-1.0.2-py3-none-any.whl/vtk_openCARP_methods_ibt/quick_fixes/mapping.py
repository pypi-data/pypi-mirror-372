from ..vtk_methods.exporting import vtk_unstructured_grid_writer
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ..vtk_methods.mapper import cell_array_mapper
from ..vtk_methods.reader import smart_reader

rescale_mesh=smart_reader("/Users/pm930l/Projects/data/Joni_volume/LA_vol_with_fiber_res.vtk")
orig_mesh=smart_reader("/Users/pm930l/Projects/data/Joni_volume/LA_vol_with_fiber.vtk")
mapped_mesh=cell_array_mapper(orig_mesh,rescale_mesh,"LA_vol_with_fiber_res_mapped.vtk","all")
vtk_unstructured_grid_writer("/Users/pm930l/Projects/data/Joni_volume/LA_vol_with_fiber_res_mapped.vtk",mapped_mesh)