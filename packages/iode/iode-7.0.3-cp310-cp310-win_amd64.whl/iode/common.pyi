from .iode_cython import EqMethod as EqMethod, EqTest as EqTest, IodeFileType as IodeFileType, IodeType as IodeType, TableLang as TableLang
from enum import IntEnum

PeriodICITY_LIST: list[str]
PRINT_DEF_TABLES: tuple[str, str]

class PrintTablesAs(IntEnum):
    FULL: int
    TITLES: int
    COMPUTED: int

PRINT_DEF_EQUATIONS: tuple[str, str, str]

class PrintEquationsAs(IntEnum):
    EQ_ONLY: int
    EQ_COMMENTS: int
    EQ_COMMENTS_ESTIMATION: int

PRINT_DEF_EQ_LEC: tuple[str, str, str]

class PrintEquationsLecAs(IntEnum):
    AS_IS: int
    COEFFS_TO_VALUES: int
    COEFFS_TO_VALUES_TTEST: int

IODE_DATABASE_TYPE_NAMES: list[str]
IODE_FILE_TYPE_NAMES: list[str]
IODE_LANGUAGES_LIST: list[str]
EQUATION_METHODS_LIST: list[str]
EQ_TEST_NAMES: tuple[str, ...]
SIMULATION_INITIALIZATION_METHODS: tuple[str, ...]
SIMULATION_SORT_ALGORITHMS: tuple[str, ...]
PRINT_FORMATS: tuple[str, ...]
IMPORT_FORMATS: tuple[str, ...]
EXPORT_FORMATS: tuple[str, ...]
WRITE_FILE_EXT: tuple[str, ...]
GRAPHS_COLORS: tuple[str, ...]
IODE_FONTS: tuple[str, ...]

class FileType:
    def __init__(self, name: str, extensions: list[str]) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def extensions(self) -> list[str]: ...

IODE_FILE_TYPES: list[FileType]
