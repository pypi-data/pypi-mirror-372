from pathlib import Path

def view_workspace(directory_path: str | Path = None, depth: int = 0):
    '''
    Open the Graphical User Interface to view and edit the IODE databases.

    Parameters
    ----------
    directory_path: str or Path, optional
        Path to the project directory. Defaults to current directory.
    depth : int, optional
        Stack depth where to look for variables. 
        Defaults to 0 (where this function was called).

    Examples
    --------
    >>> from iode import comments, equations, identities, lists, scalars, tables, variables
    >>> from iode import SAMPLE_DATA_DIR, view_workspace
    >>> comments.load(f"{SAMPLE_DATA_DIR}/fun.cmt")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.cmt
    317 objects loaded 
    >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.eqs
    274 objects loaded
    >>> identities.load(f"{SAMPLE_DATA_DIR}/fun.idt")    # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.idt
    48 objects loaded
    >>> lists.load(f"{SAMPLE_DATA_DIR}/fun.lst")         # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.lst
    17 objects loaded
    >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.scl
    161 objects loaded
    >>> tables.load(f"{SAMPLE_DATA_DIR}/fun.tbl")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.tbl
    46 objects loaded 
    >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")    # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.var
    394 objects loaded 

    >>> # will open a viewer showing all IODE databases
    >>> view_workspace()                                # doctest: +SKIP

    >>> # will open a viewer showing the content of the SAMPLE_DATA_DIR directory
    >>> view_workspace(SAMPLE_DATA_DIR)                 # doctest: +SKIP
    '''
