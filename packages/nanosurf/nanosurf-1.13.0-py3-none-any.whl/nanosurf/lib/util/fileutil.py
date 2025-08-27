""" Some helpful file and folder functions
Copyright Nanosurf AG 2021
License - MIT
"""
import os
import pathlib
import platform
from datetime import datetime

if platform.version() != "Nanosurf_Linux":
    from PySide6.QtWidgets import QApplication
    from PySide6 import QtWidgets

def create_filename_with_timestamp(base_name: str, extension: str = '.dat', separator: str = "_") -> str:
    """Make filename"""
    current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = base_name + separator + current_datetime + extension
    return filename

def create_folder(file_path: pathlib.Path) -> bool:
    """ Make sure the folder exists. 
    If needed, it  creates the intermediate directories starting from root.
    """
    done = False
    try:
        if not file_path.is_dir():
            os.makedirs(file_path, exist_ok=True)
        done = file_path.is_dir()
    except IOError:
        pass
    return done

def create_unique_folder(base_name: str, folder: pathlib.Path, add_timestamp: bool = True, separator: str = '_') -> pathlib.Path:
    """Create a unique folder.  The folder name has the structure of 'base_name_timestamp_index'
    The timestamp is optional, set argument add_timestamp=False to suppress it.
    A index is added, if the base_name folder (with optional timestamp) is not unique already. 
    The index starts at zero and is incremented until a unique name is found.

    Parameter
    ---------
    base_name: str
        The new folder name has the structure of 'base_name_timestamp_index'
    folder: pathlib.Path
        The folder in which the new subfolder with the unique name shall be created
    add_timestamp: bool, optional, defaults to True
        If set to True, a timestamp in the format of %Y%m%d-%H%M%S is added
    separator : str, optional, defaults to '_'
        The separation character use to separate parts of the folder name. 

    Result
    ------
        filepath: pathlib.Path
            path object to newly created folder. If creation was not successful the return value is None
    """
    if add_timestamp:
        base_name = create_filename_with_timestamp(base_name, extension="", separator=separator)

    done = create_folder(folder)
    if done:
        data_folder_name = base_name
        filepath = pathlib.Path(folder) / pathlib.Path(data_folder_name)
        i = 0
        while filepath.is_dir():
            data_folder_name = f"{base_name}_{i:03d}"
            filepath = pathlib.Path(folder) / pathlib.Path(data_folder_name)
            i += 1
        done = create_folder(filepath)
    if not done:
        filepath = None
    return filepath

def create_unique_filename(base_name: str, folder: pathlib.Path, suffix:str, add_timestamp: bool = True, separator: str = '_', max_index=1000) -> pathlib.Path:
    """Create a unique filename.  The new file name has the structure of 'base_name_timestamp_index.suffix'
    The timestamp is optional, set argument add_timestamp=False to suppress it.
    A index is added, if the base_name filename (with optional timestamp) is not unique already. 
    The index starts at zero and is incremented until a unique name is found.
    No file is created only the unique file name is provided.

    Parameter
    ---------
    base_name: str
        The new file name has the structure of 'base_name_timestamp_index'
    folder: pathlib.Path
        The folder in which the new filename with the unique name shall be created
        If the folder does not exists it will be created
    suffix: string
        The file suffix to add at the end
    add_timestamp: bool, optional, defaults to True
        If set to True, a timestamp in the format of %Y%m%d-%H%M%S is added
    separator : str, optional, defaults to '_'
        The separation character use to separate parts of the folder name. 

    Result
    ------
        filepath: pathlib.Path
            path object to unique file name or None if it could not be created
    """

    if not folder.is_dir():
        if not create_folder(folder):
            return None

    if add_timestamp:
        base_name = create_filename_with_timestamp(base_name, extension="", separator=separator)

    i = 0
    filepath = folder / pathlib.Path(f"{base_name}_{i:03d}").with_suffix(suffix) 
    while filepath.is_file() and i < max_index:
        filepath = folder / pathlib.Path(f"{base_name}_{i:03d}").with_suffix(suffix) 
        i += 1

    if not filepath.is_file(): 
        return filepath
    return None 

if platform.version() != "Nanosurf_Linux":
    def ask_folder(title:str = None, start_dir:pathlib.Path = None) -> pathlib.Path:
        """ Prompt user to select a folder. Presents the user a dialog to select a folder or create a new one. 

        Parameter
        ---------
        title: optional, str
            defines the dialog title
        start_dir: optional, pathlib.Path
            The folder which is presented to the user at start.
            If omitted its the current working folder.


        Result
        ------
            dir_path: pathlib.Path
                A full path object to the selected created folder.
                Or None, if the user aborts the dialog
        """
        if start_dir is None: start_dir = os.getcwd()
        if title is None: title = 'Select a folder'

        if not QApplication.instance(): _ = QApplication([]) 

        selected_filename = QtWidgets.QFileDialog.getExistingDirectory(None, title, dir=str(start_dir))
        if selected_filename != '':
            dest_name = pathlib.Path(selected_filename)
            return dest_name
        return None

    def ask_open_file(title:str = None, start_dir:pathlib.Path = None, suffix_mask:str = None) -> pathlib.Path:
        """ Prompt user to select a file. Presents the user a dialog to select an existing. 

        Parameter
        ---------
        title: optional, str
            defines the dialog title
        start_dir: optional, pathlib.Path
            The folder which is presented to the user at start.
            If omitted its the current working folder.
        suffix_mask: optional, str
            This defines a filter for shown file type. 
            e. g: '*.pdf' would only show files with ending 'pdf'
            If omitted, it shows all files

        Result
        ------
            file_path: pathlib.Path
                A full path object to the selected file.
                Or None, if the user aborts the dialog
        """    
        if start_dir is None: start_dir = os.getcwd()
        if title is None: title = 'Select a file'
        if suffix_mask is None: file_filter="(*.*)"
        else: file_filter = f"(*.{suffix_mask})"

        if not QApplication.instance(): _ = QApplication([]) 
        selected_filename = QtWidgets.QFileDialog.getOpenFileName(None, title, dir=str(start_dir), filter=file_filter)
        if selected_filename[0] != '':
            dest_name = pathlib.Path(selected_filename[0])
            return dest_name
        return None

    def ask_save_file(title:str = None, target_dir:pathlib.Path = None, default_file:pathlib.Path = None, suffix_mask:str = None) -> pathlib.Path:
        """ Prompt user to define a file to save to. Presents the user a dialog to select an existing file or to define one. 

        Parameter
        ---------
        title: optional, str
            defines the dialog title
        start_dir: optional, pathlib.Path
            The folder which is presented to the user at start.
            If omitted its the current working folder.
        suffix_mask: optional, str
            This defines a filter for shown file type. 
            e. g: '*.pdf' would only show files with ending 'pdf'
            If omitted, it shows all files

        Result
        ------
            file_path: pathlib.Path
                A full path object to the selected file.
                Or None, if the user aborts the dialog
        """    
        if target_dir is None: target_dir = os.getcwd()
        if title is None: title = 'Define or select a file'
        if suffix_mask is None: file_filter="(*)"
        else: file_filter = f"({suffix_mask})"
        if default_file is None: default_file = "default"
        target_path = pathlib.Path(target_dir) / pathlib.Path(default_file)

        if not QApplication.instance(): 
            _ = QApplication([]) 
        selected_filename = QtWidgets.QFileDialog.getSaveFileName(None, title, dir=str(target_path), filter=file_filter)
        if selected_filename[0] != '':
            dest_name = pathlib.Path(selected_filename[0])
            return dest_name
        return None