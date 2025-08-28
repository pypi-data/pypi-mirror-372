from . import run_gmsh
import pathlib
from . import mesh
import lnmmeshio
import tempfile
import meshio
from .reorder import reorder


def combine_colored_stl_files(*stl_files: pathlib.Path) -> meshio.Mesh:
    """
    Combine multiple colored STL files into a single mesh that is returned.
    """
    return mesh.merge_colored_stl(*stl_files)[0]


def mesh_colored_stl_files(*stl_files: pathlib.Path, mesh_size: float) -> meshio.Mesh:
    """
    Generate a mesh from multiple colored STL files

    Parameters
    ----------
    *stl_files : pathlib.Path
        Paths to the STL files to be merged.

    mesh_size : float
        The target size for the mesh elements.

    Returns
    -------
    lnmmeshio.Discretization
        The generated mesh.
    """
    assert len(stl_files) > 0, "At least one STL file must be provided."

    with tempfile.TemporaryDirectory() as tmpdir:
        # merge stl files into a single mesh file
        gmsh_file = pathlib.Path(tmpdir) / "merged.mesh"
        m, surface_loops = mesh.merge_colored_stl(*stl_files)
        lnmmeshio.write_mesh(str(gmsh_file), m)

        # remesh file using Gmsh
        return run_gmsh.remesh_file(gmsh_file, surface_loops, mesh_size)
