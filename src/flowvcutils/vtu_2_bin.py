import vtk
import numpy as np
import sys
import logging.config
import logging.handlers
from flowvcutils.jsonlogger import settup_logging
import argparse
import os
import shutil

logger = logging.getLogger("vtu_2_bin")


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

    def save_file(self, output_root, file_name):
        """Save a cordinates binary file in the specified location.

        File Name: {output_root}_coordinates.bin
        """
        file_path = create_file_path(
            root=output_root, file_name=file_name, file_type="coordinates"
        )
        fout = open(file_path, "wb")
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

    def save_file(self, output_root, file_name):
        """Save a cordinates binary file in the specified location.

        File Name: {output_root}_connectivity.bin
        """
        file_path = create_file_path(
            root=output_root, file_name=file_name, file_type="connectivity"
        )
        fout = open(file_path, "wb")
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

    def save_file(self, output_root, file_name, offset=0):
        """Save the adjacency binary file in the specified location.

        File Name: {output_root}_adjacency.bin
        """
        file_path = create_file_path(
            root=output_root, file_name=file_name, file_type="adjacency"
        )
        fout = open(file_path, "wb")
        (self.n_elements * np.ones(1, dtype=np.int32)).tofile(fout)
        ((self.adjacency) + offset).tofile(fout)
        fout.close()

        logger.debug(f"First 50 adjacency rows: \n {((self.adjacency))[:50, :]}")


def vtk_to_connectivity_and_coordinates(
    input_root,
    output_root,
    file_name,
    start=0,
    num_digits=5,
    offset=0,
    extension=".vtu",
):
    """Create connectivity, coordinates, and adjacency files

    vtk_filename: name of input file
    output_root: file path to save created files
    offset: Set offset to 1 if node IDs should be 1 indexed
    extension: input file extension (default .vtu)
    """
    logger.debug("starting vtk_to_connectivity_and_cordinates")
    reader = reader_selection(extension)
    logger.debug("reader selected")
    # Select first .vtu file to create coordinates, adjacency, and connectivity files
    first_file_path = os.path.join(
        input_root, f"{file_name}{start:0{num_digits}d}{extension}"
    )
    reader.SetFileName(first_file_path)
    logger.debug("reader setfilename")
    reader.Update()
    data = reader.GetOutput()
    logger.debug("data selected")
    coordinates = coordinates_file(data)
    coordinates.create_file()
    coordinates.save_file(output_root, file_name)
    logger.info(f"{coordinates.n_nodes} nodes, coordinated file created")

    connectivity = connectivity_file(data)
    connectivity.create_file()
    connectivity.save_file(output_root, file_name)

    logger.info(f"{connectivity.n_elements} elements, connectivity file saved")

    logger.info("Finding adjacency:")
    adjacency = adjacency_file(data)
    adjacency.create_file()
    adjacency.save_file(output_root, file_name, offset)


def vtk_to_bin(
    input_root,
    output_root,
    file_name,
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
    logger.info("starting vtk_to_bin")
    if not flag_fenics_zeros:
        file_num_format = "%0" + str(file_num_digits) + "d"

    for file_num in range(start, stop + 1, increment):
        logger.info(f"Writing .bin {file_num}")
        if flag_fenics_zeros:
            file_num_string = str(file_num) + "000000"
        else:
            file_num_string = file_num_format % file_num

        reader = reader_selection(extension)
        input_path = os.path.join(input_root, file_name + file_num_string + extension)
        logger.info(f"Reading..{input_path}")
        reader.SetFileName(input_path)
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
        out_file_path = create_vel_file_path(output_root, file_name, file_num)
        fout = open(out_file_path, "wb")
        out_data.tofile(fout)
        fout.close()


def strip_trailing_underscore(file_name):
    if file_name.endswith("_"):
        return file_name[:-1]
    return file_name


def create_vel_file_path(root, file_name, file_num):
    return os.path.join(
        root, strip_trailing_underscore(file_name) + "_vel." + str(file_num) + ".bin"
    )


def create_file_path(root, file_name, file_type):
    return os.path.join(
        root, strip_trailing_underscore(file_name) + "_" + file_type + ".bin"
    )
    pass


# os.path.join(output, file_name),
def process_folder(
    root, output, file_name, extension, start, stop, increment, num_digits, field_name
):
    """Create binary files from vtu files for FlowVC.

    Reference https://shaddenlab.berkeley.edu/uploads/releasenotes.pdf
    """
    vtk_to_connectivity_and_coordinates(
        input_root=root,
        output_root=output,
        file_name=file_name,
        start=start,
        num_digits=num_digits,
        offset=0,
        extension=extension,
    )

    vtk_to_bin(
        root,
        output,
        file_name,
        start,
        stop,
        increment,
        fieldname=field_name,
        n_components=3,
        file_num_digits=num_digits,
        n_pad_values=1,
        flag_fenics_zeros=0,  # if 1, then adds zeros similar to finix
        extension=extension,
    )


def process_directory(root, extension, start, stop, increment, num_digits, field_name):
    """
    Process an entire directory vtu files to .bin file.

    Goes into each sub directory.
    Runns process folder with the arguments
       file_name = subdirectory_name
       output = subdir/bin
    #WARNING: This removes the current subdirectory/bin folder if it exists
    """
    for sub_directory in os.listdir(root):
        sub_dir_path = os.path.join(root, sub_directory)
        logger.debug(f"sub_directory:{sub_directory}")
        if os.path.isdir(sub_dir_path):
            logger.info(f"Processing Directory {sub_directory}")
            bin_dir = os.path.join(sub_dir_path, "bin")
            if os.path.exists(bin_dir):
                shutil.rmtree(bin_dir)

            os.makedirs(bin_dir)

            process_folder(
                root=sub_dir_path,
                output=bin_dir,
                file_name=sub_directory,
                extension=extension,
                start=start,
                stop=stop,
                increment=increment,
                num_digits=num_digits,
                field_name=field_name,
            )


class Parser:
    """Handles CLI argument parsing."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Process VTU files to a .bin format."
        )
        self._setup_arguments()

    def _setup_arguments(self):
        """Define CLI arguments."""
        self.parser.add_argument(
            "--process",
            choices=["folder", "directory"],
            default="folder",
            help=(
                "Processing mode: 'folder' for a single folder or 'directory'"
                "to process subdirectories (default: 'folder')."
            ),
        )

        self.parser.add_argument(
            "start",
            type=int,
            help="Starting index for the processing files (required).",
        )
        self.parser.add_argument(
            "stop",
            type=int,
            help=("Stopping index for the processing files (required)."),
        )
        self.parser.add_argument(
            "file_name",
            type=str,
            nargs="?",
            default=os.path.basename(os.getcwd()),
            help=(
                "Base file name (e.g., steady_ for steady_00000.vtu)"
                "(required for folder)."
            ),
        )

        self.parser.add_argument(
            "--root",
            default=os.getcwd(),
            help="Input directory with the VTU files (default: current directory).",
        )
        self.parser.add_argument(
            "--output",
            default=os.getcwd(),
            help="Output directory (default: current directory).",
        )

        self.parser.add_argument(
            "--extension",
            type=str,
            default=".vtu",
            help="File extension (default: '.vtu').",
        )

        self.parser.add_argument(
            "--increment",
            type=int,
            default=50,
            help="Increment between each vtu file (default = 50).",
        )
        self.parser.add_argument(
            "--num_digits",
            default=5,
            type=int,
            help="Digits in file name (e.g., 5 for test_00100.vtu). (default: 5).",
        )
        self.parser.add_argument(
            "--field_name",
            default="velocity",
            help="Field name for velocity data (default: 'velocity').",
        )

    def parse_arguments(self, args=None):
        """Parse the CLI arguments."""
        return self.parser.parse_args(args)


class Router:
    """Routes the execution based on CLI arguments."""

    def __init__(self, args):
        self.args = args

    def route(self):
        """Route to the appropriate processing function."""
        if self.args.process == "folder":
            process_folder(
                root=self.args.root,
                output=self.args.output,
                file_name=self.args.file_name,
                extension=self.args.extension,
                start=self.args.start,
                stop=self.args.stop,
                increment=self.args.increment,
                num_digits=self.args.num_digits,
                field_name=self.args.field_name,
            )
        elif self.args.process == "directory":
            process_directory(
                root=self.args.root,
                # output=self.args.output,
                # file_name=self.args.file_name,
                extension=self.args.extension,
                start=self.args.start,
                stop=self.args.stop,
                increment=self.args.increment,
                num_digits=self.args.num_digits,
                field_name=self.args.field_name,
            )
        else:
            raise ValueError("Invalid process type specified.")


def main():
    """Create binary files from vtu files for FlowVC.

    Reference https://shaddenlab.berkeley.edu/uploads/releasenotes.pdf
    """
    settup_logging()
    # Parse a CLI flag to enable setting the log level from the CLI
    parser = Parser()
    args = parser.parse_arguments()
    router = Router(args)
    router.route()


if __name__ == "__main__":
    main()
