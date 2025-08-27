""" This is a file with auxiliary functions for GUI template using Nanosurf Studio Style
Copyright Nanosurf AG 2021
License - MIT
"""
import pathlib
import platform


def savedata_txt(file_name: pathlib.Path, data, header:str="", separator="\t"):
    """ Save data matrix in multiple columns: 
    
        Parameters
        ----------
        file_name:
            string or Path() with path to file which should be created
        data[channel][data]:
            fist dimension = channels, second dimension = data stream
            All kind of data classes are supported as long as it can be converted to text by str() operator
            and its can be access with data[x][y] operator. All streams have to be of same length.
        header, optional:
            Text string to be inserted at first line in file
        separator, optional:
            defines the string used to separate columns, default is '\t' tab

        Return
        ------
            None, but raise exception if file could not be written to or misaligned data
    """
    with open(file_name, 'w') as f:
        if header != "":
            f.write(header+"\n")
        for i in range(len(data[0])):
            write_string = ""
            for j in range(len(data)):
                if j == len(data)-1:
                    write_string =  write_string + str(data[j][i]) + "\n"
                else:
                    write_string =  write_string + str(data[j][i]) + separator
            f.write(write_string)
        f.close()

def loaddata_txt(file_name: pathlib.Path, vertical = True, skip_header: int = 0, separator="\t") -> list:
    """ Load data matrix from file of multiple columns or rows. : 
    
        Parameters
        ----------
        file_name: str or Path()
            Path to file which should be created
        vertical: bool, optional
            if True the file has columns of data, otherwise it is assumed that the data are organized in rows 
        skip_header, optional:
            if provided, the number of header lins to skip before the data
        separator, optional:
            defines the string used to separate columns or rows, default is '\t' tab

        Result
        ------
        list[channel[stream]: 
    """    
    result = []
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if skip_header <= 0:
                sline = line.rstrip()
                splitline = sline.split(separator)
                floatline = [float(i) for i in splitline]
                result.append(floatline)
            else:
                skip_header -= 1
    if vertical:
        result = list(map(list, zip(*result)))
    return result


if platform.version() != "Nanosurf_Linux":
    import pyqtgraph.exporters

    def saveplot_png(file_name: pathlib.Path, plotitem:pyqtgraph.PlotItem, size:int = 0) -> pathlib.Path:
        """ Save a 'pyqtgraph' plot item to file: 
        
            Parameters
            ----------
            file_name:
                string or Path() with path to file which should be created, if no suffix is provided '.png' is added to the path
            plotitem: pyqtgraph.PlotItem
                The plot which shall be saved
            size, optional:
                If provided, it defines the size of the image in pixes. 

            Return
            ------
                file_name: fine used path is returned
                Exceptions are raised, if file could not be written to if export could not be done
        """
        if isinstance(file_name, str):
            file_name = pathlib.Path(file_name)
        if file_name.suffix == "":
            file_name.with_suffix('.png')

        exporter = pyqtgraph.exporters.ImageExporter(plotitem)
        if size > 0:
            exporter.parameters()['width'] = size   # (note this also affects height parameter)
        exporter.export(str(file_name))
        return file_name

    def save_results(file_name: pathlib.Path, resulttable: 'NSFNameValueTable'):    
        """ Save a 'pyqtgraph' plot item to file: 
        
            Parameters
            ----------
            file_name:
                string or Path() with path to file which should be created, if no suffix is provided '.png' is added to the path
            resulttable: NSFNameValueTable
                The table content which shall be saved.

            Return
            ------
                Exceptions are raised, if file could not be written
        """
        with open(file_name, 'w') as f:
            for id in range(resulttable.rowCount()):
                name_str = resulttable.item(id,0).text()
                val_str = resulttable.item(id,1).text()
                result_string = name_str + "; "+ val_str +("\n")
                f.write(result_string)
            f.close()
