import vtk
import numpy as np
import sys
import logging
import argparse

logger = logging.getLogger(__name__)


def reader_selection(extension):
    """Select the appropriate reader based on the file type."""
    if extension == ".vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif extension == ".vtu":
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif extension == ".vtk":
        reader = vtk.vtkDataSetReader()
    elif extension == ".pvtu":
        reader = vtk.vtkXMLPUnstructuredGridReader()
    else:
        raise ValueError("unsuported file type inputed")
    return reader


class coordinates_file:
    """Create a cordinates binary file.

    File Name: {output_root}_coordinates.bin
    Format: [n (int), x_0 (double), y_0, z_0, x_1, y_1 ... z_n]
    n (int): number of nodes
    x_0, y_0 z_0 (3 doubles): the cordinates of each node
    reference: https://shaddenlab.berkeley.edu/software.html
    """

    def __init__(self, data):
        """Store data as an atribute of self."""
        self.data = data

    def create_file(self):
        """Create the cordinates file."""
        self.n_nodes = self.data.GetNumberOfPoints()
        self.coordinates = np.zeros(self.n_nodes * 3)
        for i in range(self.n_nodes):
            self.data.GetPoint(i, self.coordinates[i * 3 : i * 3 + 3])

    def save_file(self, output_root):
        """Save a cordinates binary file in the specified location.

        File Name: {output_root}_coordinates.bin
        """
        fout = open(output_root + "_coordinates.bin", "wb")
        logger.debug(f"n_nodes data type: {type(self.n_nodes)}")
        (self.n_nodes * np.ones(1, dtype=np.int32)).tofile(fout)
        self.coordinates.tofile(fout)
        fout.close()


class connectivity_file:
    """Create a connectivity binary file.

    File Name: {output_root}_connectivity.bin
    Format: [e (int), i_00 (int), i_01, i_02, i03, i_10, i_11, ... i_n3]
    e (int): number of elements
    i_00 - i03 (4 ints): the 4 nodes that make up the 0ith element.
    reference: https://shaddenlab.berkeley.edu/software.html
    """

    def __init__(self, data):
        """Store data as an atribute of self."""
        self.data = data

    def create_file(self):
        """Create the cordinates file."""
        self.n_elements = self.data.GetNumberOfCells()
        self.connectivity = np.zeros(self.n_elements * 4, dtype=np.int32)
        count = 0
        for i in range(self.n_elements):
            tmp = vtk.vtkIdList()
            self.data.GetCellPoints(i, tmp)
            for j in range(4):
                self.connectivity[4 * count + j] = tmp.GetId(j)
            count = count + 1
        # self.connectivity += offset

    def save_file(self, output_root):
        """Save a cordinates binary file in the specified location.

        File Name: {output_root}_connectivity.bin
        """
        fout = open(output_root + "_connectivity.bin", "wb")
        (self.n_elements * np.ones(1, dtype=np.int32)).tofile(fout)
        self.connectivity.tofile(fout)
        fout.close()


class adjacency_file:
    """Create a ajacency binary file.

    File Name: {output_root}_adjacency.bin
    Format: [e (int), e_00 (int), e_01, e_02, e03, e_10, e_11, ... e_n3]
    e (int): number of elements
    e_00 - e03 (4 ints): the 4 elements that share a common face with .

    The numbering of elements needs to match connectivity.bin order
    Boundary elements without shared faces should be set to -1
    reference: https://shaddenlab.berkeley.edu/software.html
    """

    def __init__(self, data):
        """Store data as an atribute of self."""
        self.data = data

    def create_file(self):
        """Create adjacency file."""
        self.n_elements = self.data.GetNumberOfCells()
        self.adjacency = -1 * np.ones((self.n_elements, 4), dtype=np.int32)
        node_ids = vtk.vtkIdList()
        node_ids.SetNumberOfIds = 4
        face_ids = vtk.vtkIdList()
        face_ids.SetNumberOfIds = 3
        progress = 0
        for i in range(self.n_elements):
            if ((i * 100) / self.n_elements) > progress:
                logger.info(f"progress {progress}")
                sys.stdout.flush()
                progress += 5
            self.data.GetCellPoints(i, node_ids)
            for j in range(4):
                for k in range(3):
                    face_ids.InsertId(k, node_ids.GetId((j + k + 2) % 4))
                shared_cells = vtk.vtkIdList()
                self.data.GetCellNeighbors(i, face_ids, shared_cells)
                if shared_cells.GetNumberOfIds() == 0:
                    self.adjacency[i, j] = -1
                else:
                    self.adjacency[i, j] = shared_cells.GetId(0)
        logger.info("progress 100")
        # self.connectivity += offset

    def save_file(self, output_root, offset=0):
        """Save the adjacency binary file in the specified location.

        File Name: {output_root}_adjacency.bin
        """
        fout = open(output_root + "_adjacency.bin", "wb")
        (self.n_elements * np.ones(1, dtype=np.int32)).tofile(fout)
        ((self.adjacency) + offset).tofile(fout)
        fout.close()

        logger.debug(f"First 50 adjacency rows: \n {((self.adjacency))[:50, :]}")


def vtk_to_connectivity_and_coordinates(
    vtk_filename,
    output_root,
    offset=0,
    extension=".vtu",
):
    """Create connectivity, coordinates, and adjacency files

    vtk_filename: name of input file
    output_root: file path to save created files
    offset: Set offset to 1 if node IDs should be 1 indexed
    extension: input file extension (default .vtu)
    """

    reader = reader_selection(extension)
    logger.debug("reader selected")
    reader.SetFileName(vtk_filename)
    logger.debug("reader setfilename")
    reader.Update()
    data = reader.GetOutput()
    logger.debug("data selected")
    coordinates = coordinates_file(data)
    coordinates.create_file()
    coordinates.save_file(output_root)
    logger.info(f"{coordinates.n_nodes} nodes, coordinated file created")

    connectivity = connectivity_file(data)
    connectivity.create_file()
    connectivity.save_file(output_root)

    logger.info(f"{connectivity.n_elements} elements, connectivity file saved")

    logger.info("Finding adjacency:"),
    adjacency = adjacency_file(data)
    adjacency.create_file()
    adjacency.save_file(output_root, offset)


def vtk_to_bin(
    vtk_root,
    output_root,
    start,
    stop,
    increment,
    fieldname="Velocity",
    n_components=3,
    file_num_digits=5,
    n_pad_values=1,
    flag_fenics_zeros=0,
    extension=".vtu",
):
    """Create a velocity binary file.

    n_components: set to 1 for scalar, 3 for vector
    file_num_digits: number of digits in vtk filename
        e.g. for "test.00100.vtk", file_num_digits=5
    n_pad_values: number of zeros at beginning of bin file
      (needed to match timestamp from Simvascular output
    """
    if not flag_fenics_zeros:
        file_num_format = "%0" + str(file_num_digits) + "d"
    for file_num in range(start, stop + 1, increment):
        logger.info(f"Writing .bin {file_num}")
        if flag_fenics_zeros:
            file_num_string = str(file_num) + "000000"
        else:
            file_num_string = file_num_format % file_num

        reader = reader_selection(extension)
        logger.info(f"Reading..{vtk_root + file_num_string + extension}")
        reader.SetFileName(vtk_root + file_num_string + extension)
        reader.Update()
        data = reader.GetOutput()

        n_nodes = data.GetNumberOfPoints()

        # First n_pad_values in out_data set to zero
        out_data = np.zeros(n_nodes * n_components + n_pad_values)

        values = data.GetPointData().GetArray(fieldname)

        for i in range(n_nodes):
            values.GetTuple(
                i,
                out_data[
                    i * n_components
                    + n_pad_values : (i + 1) * n_components
                    + n_pad_values
                ],
            )

        fout = open(output_root + "." + str(file_num) + ".bin", "wb")
        out_data.tofile(fout)
        fout.close()


def main():
    """Create binary files from vtu files for FlowVC.

    Reference https://shaddenlab.berkeley.edu/uploads/releasenotes.pdf
    """
    # root_dir = "../../../../Data/CFD-Solutions/Interpolated-File-Series/"
    # output_dir = "../../../../Data/CFD-Solutions/Bin-File-Series/"
    root_dir = "/home/bkm82/masters/ECMO/Data/CFD-Solutions/Interpolated-File-Series/"
    output_dir = "/home/bkm82/masters/ECMO/Data/CFD-Solutions/Bin-File-Series/"

    vtk_to_connectivity_and_coordinates(
        root_dir + "interpolated_velocity_rotated_0.vtu",
        output_dir + "interpolated_velocity_roated",
        offset=0,
        extension=".vtu",
    )

    vtk_to_bin(
        root_dir + "interpolated_velocity_rotated_",
        output_dir + "interpolated_velocity_rotated",
        0,
        19,
        1,
        fieldname="Velocity_No_Slip",
        n_components=3,
        file_num_digits=1,
        n_pad_values=1,
        flag_fenics_zeros=0,  # if 1, then adds zeros similar to Fenics adding zeros to the end of the file name
        extension=".vtu",
    )


if __name__ == "__main__":
    # Parse a CLI flag to enable setting the log level from the CLI
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-log",
        "--loglevel",
        dest="loglevel",
        default="INFO",
        help="select the log level (DEBUG, INFO, WARNING, CRITICAL)",
    )

    args = parser.parse_args()
    loglevel = args.loglevel
    logging.basicConfig(level=loglevel)
    main()