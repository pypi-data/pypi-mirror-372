from collections.abc import Iterable as Iterable
from iode.iode_cython import AdjustmentMethod as AdjustmentMethod, CythonCorrelationMatrix as CythonCorrelationMatrix, CythonEditAndEstimateEquations as CythonEditAndEstimateEquations, EqMethod as EqMethod, cython_dickey_fuller_test as cython_dickey_fuller_test, cython_dynamic_adjustment as cython_dynamic_adjustment
from iode.iode_database.equations_database import Equations as Equations
from iode.iode_database.scalars_database import Scalars as Scalars
from iode.iode_database.variables_database import variables as variables
from iode.objects.equation import Equation as Equation
from iode.time.period import Period as Period
from iode.time.sample import Sample as Sample
from iode.util import enable_msgs as enable_msgs, suppress_msgs as suppress_msgs
from typing import Any, Self

Self = Any

def dynamic_adjustment(method: AdjustmentMethod | str, eqs: str, c1: str = 'c1', c2: str = 'c2') -> str:
    '''
    Transform a LEC equation to add a dynamic adjustment.
    
    Two methods can be used. Given the equation :math:`LHS = RHS`, we have:
    
        - **Partial Adjustment** (PARTIAL): :math:`d(LHS) = c1 * (RHS - (LHS)[-1])`
        - **Error Correction Model** (ERROR_CORRECTION): :math:`d(LHS) = c1 * d(RHS) + c2 * (RHS -LHS)[-1]`
    
    Parameters
    ----------
    method: AdjustmentMethod or str 
        Method used for the dynamic adjustment. 
        Possible values are PARTIAL or ERROR_CORRECTION.
    eqs: str
        LEC equation to dynamically adjust.
    c1: str, optional        
        Name of the first coefficient.
        Default to "c1".
    c2: str, optional    
        Name of the second coefficient. 
        Not used with the *Partial Adjustment* method.
        Default to "c2".

    Returns
    -------
    str
        Dynamically adjusted equation.

    Examples
    --------
    >>> from iode import SAMPLE_DATA_DIR, equations, dynamic_adjustment, AdjustmentMethod
    >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.eqs
    274 objects loaded 
    >>> lec = equations["ACAF"].lec                         # doctest: +NORMALIZE_WHITESPACE
    >>> lec
    \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'
    
    Partial Adjustment

    >>> partial_adjust_eq = dynamic_adjustment(AdjustmentMethod.PARTIAL, lec)
    >>> partial_adjust_eq
    \'d((ACAF/VAF[-1])) := c1 * (acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995) -((ACAF/VAF[-1]))[-1])\'

    Error Correction Model

    >>> error_corr_adjust_eq = dynamic_adjustment(AdjustmentMethod.ERROR_CORRECTION, lec)
    >>> error_corr_adjust_eq
    \'d((ACAF/VAF[-1])) := c1 * d(acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)) + c2 * (acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995) -(ACAF/VAF[-1]))[-1]\'
    '''
def dickey_fuller_test(lec: str, drift: bool, trend: bool, order: int) -> Scalars:
    '''
    Dickey-Fuller tests.

    Tests are saved in scalars whose name is composed of the prefix *df_* and the name of the first series 
    appearing in the formula to be tested. For example, the test for the formula :math:`d(A0GR+A0GF)` is `df_a0gr`.

    Parameters
    ----------
    lec: str
        LEC form to be tested.
    drift: bool
        Whether or not the formula to be estimated must incorporate a constant term. 
    trend: bool
        Whether or not the formula to be estimated should incorporate a trend term.
    order: int 
        Order of the polynomial to be estimated to obtain the tests.
    
    Returns
    -------
    Scalars
        Scalars database containing the results of the Dickey-Fuller tests.

    Examples
    --------
    >>> from iode import SAMPLE_DATA_DIR, scalars, variables
    >>> from iode import dickey_fuller_test
    >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Loading .../fun.var
    394 objects loaded

    >>> # dickey_fuller_test("ACAF", True, True, 3) estimates the equation:
    >>> #     d(ACAF) := df_ * ACAF[-1] +            
    >>> #     df_d +            (DRIFT)          
    >>> #     df_t * t +        (TREND)            
    >>> #     df1 * d(ACAF[-1]) + df2*d(ACAF[-2]) + df3*d(ACAF[-3])  (ORDER)
    >>> df_scalars = dickey_fuller_test("ACAF", True, True, 3)
    Estimating : iteration 1 (||eps|| = 2.20454)
    Estimating : iteration 2 (||eps|| = 2.39047e-10)
    Solution reached after 2 iteration(s). Creating results file ...
    >>> df_scalars.get_names("df*")
    [\'df1\', \'df2\', \'df3\', \'df_\', \'df_d\', \'df_t\']
    >>> # note: the function dickey_fuller_test() returns a separated Scalars database.
    >>> #       The global database scalars is left unchaged
    >>> scalars.get_names("df*")
    []
    >>> # order 0
    >>> df_scalars["df_"]
    Scalar(0.0132523, 0.0845155, 0.0845155)
    >>> # drift
    >>> df_scalars["df_d"]
    Scalar(13.0806, 1, 6.78675)
    >>> # trend
    >>> df_scalars["df_t"]
    Scalar(-0.492697, 0.187978, 0.187978)
    >>> # order 1
    >>> df_scalars["df1"]
    Scalar(-0.120123, 0.180991, 0.180991)
    >>> # order 2
    >>> df_scalars["df2"]
    Scalar(-0.476959, 0.154505, 0.154505)
    >>> # order 3
    >>> df_scalars["df3"]
    Scalar(-0.211047, 0.170708, 0.170708)
    '''

class CorrelationMatrix:
    def __init__(self) -> None: ...
    @classmethod
    def get_instance(cls) -> Self: ...
    @property
    def shape(self) -> tuple[int, int]: ...
    @property
    def names(self) -> list[str]: ...
    def name(self, index: int) -> str: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key: tuple[int, int]) -> float: ...
    def __setitem__(self, key, value) -> None: ...
    def __delitem__(self, key) -> None: ...

class EditAndEstimateEquations:
    """
    Special separate Equations and Scalars databases to make estimations and merge results 
    into the global Scalars database if results are satisfying.

    Warnings
    --------
    Dedicated to be used only by the developers in the code of the Graphical User Interface for IODE
    """
    def __init__(self, from_period: str | Period = None, to_period: str | Period = None) -> None: ...
    @property
    def sample(self) -> Sample:
        '''
        Estimation sample.

        Parameters
        ----------
        value: str or slice(str, str) or tuple(str, str) or Sample
            New estimation sample as either string \'start_period:last_period\' or 
            slice \'start_period\':\'last_period\' or tuple \'start_period\', \'last_period\'.
        
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> variables.sample
        Sample("1960Y1:2015Y1")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations()
        >>> estimation.sample
        Sample("1960Y1:2015Y1")
        >>> estimation.sample = "1980Y1:1996Y1"
        >>> estimation.sample
        Sample("1980Y1:1996Y1")
        '''
    @sample.setter
    def sample(self, value: str | slice | tuple[str | Period, str | Period] | Sample): ...
    @property
    def block(self) -> str:
        '''
        Update the \'block\', \'kdb_eqs\', \'kdb_scl\', \'v_equations\' and \'current_eq\' C++ attributes 
        given the passed values for the \'block\' and \'current_eq_name\'. 
        
        What the C++ method set_block() does:

            - Step 1:  reset attributes \'block\', \'v_equations\' and \'current_eq\'
            - Step 2:  generate a list of equations names from the passed argument \'block\'
            - Step 3:  add the current equation name to the block if not referenced in it 
            - Step 4:  check each name if is valid. If there is an invalid name, throw an error
            - Step 5:  for each equation name from the block:
                       a. check if the equation is already present in the local database \'kdb_eqs\':
                       - no  -> check if in the global database:
                                - yes -> copy equation from the global database to \'kdb_eqs\'. 
                                - no  -> add a new equation with LEC \'<name> := 0\' to \'kdb_eqs\'.
                       - yes -> does nothing.
                       b. add the equation name to the vector \'v_equations\'.
            - Step 6: copy the list of equations names separated by \';\' to the \'block\' attribute
            - Step 7: move the equations iterator to the current equation or the first equation of the block

        Parameters
        ----------
        value: str or tuple(str, str)
            Represent both the list of equations to estimate (\'block\') and the name of the currently 
            displayed (edited) equation (in the GUI) (\'current_eq_name\').
            If the passed value is a simple string (not a tuple), \'current_eq_name\' is set to an empty string.
        
        Notes
        -----
        Equivalent to the ODE_blk_check() function from o_est.c from the old GUI (developed by Jean-Marc Paul)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")

        >>> # ====== block = ACAF;DPUH ======
        >>> # set_block("new_block", "currently_displayed_equation")
        >>> #
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'
        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'DPUH\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\']
        >>> # ---- scalars list ----
        >>> estimation.update_scalars()
        >>> scalars_res = estimation.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'ACAF\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'             
        >>> # ---- next equation ---- 
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'DPUH\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'dln (DPUH/DPUHO):=dpuh_1+dpuh_2*dln(IHU/PI5)+dln PC\'
        >>> # ---- go back to first eq ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'ACAF\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'

        >>> # ====== add a non existing equation to the block ======
        >>> # set_block("new_block", "currently_displayed_equation")
        >>> #
        >>> estimation.block = "ACAF;DPUH;TEST", "DPUH"
        >>> estimation.block
        \'ACAF;DPUH;TEST\'
        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'DPUH\', \'TEST\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\', \'TEST\']
        >>> # ---- scalars list ----
        >>> estimation.update_scalars()
        >>> scalars_res = estimation.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'DPUH\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'dln (DPUH/DPUHO):=dpuh_1+dpuh_2*dln(IHU/PI5)+dln PC\'
        >>> # ---- next equation ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'TEST\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'TEST := 0\'
        >>> # ---- next equation ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'ACAF\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'

        >>> # ====== remove an equation from the block ======
        >>> # set_block("new_block", "currently_displayed_equation")
        >>> #
        >>> estimation.block = "ACAF;TEST", "ACAF"
        >>> estimation.block
        \'ACAF;TEST\'
        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'TEST\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\', \'TEST\']
        >>> # ---- scalars list ----
        >>> estimation.update_scalars()
        >>> scalars_res = estimation.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\']
        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'ACAF\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'
        >>> # ---- next equation ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'TEST\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'TEST := 0\'

        >>> # ====== currently displayed equation not in the block -> add it to the block ======
        >>> # set_block("new_block", "currently_displayed_equation")
        >>> #
        >>> estimation.block = "ACAF;TEST", "DPUH"
        >>> estimation.block
        \'ACAF;TEST;DPUH\'
        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'TEST\', \'DPUH\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\', \'TEST\']
        >>> # ---- scalars list ----
        >>> estimation.update_scalars()
        >>> scalars_res = estimation.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'DPUH\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'dln (DPUH/DPUHO):=dpuh_1+dpuh_2*dln(IHU/PI5)+dln PC\'

        >>> # ====== some scalars does not exist yet ======
        >>> #
        >>> del scalars["dpuh_1"]
        >>> del scalars["dpuh_2"]
        >>> estimation_new_coeffs = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> # set_block("new_block", "currently_displayed_equation")
        >>> estimation_new_coeffs.block = "ACAF;DPUH", "ACAF"
        >>> # ---- equations list ----
        >>> estimation_new_coeffs.equations_list
        [\'ACAF\', \'DPUH\']
        >>> # ---- scalars list ----
        >>> estimation_new_coeffs.update_scalars()
        >>> scalars_res = estimation_new_coeffs.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> scalars_res["dpuh_1"]
        Scalar(0.9, 1, na)
        >>> scalars_res["dpuh_2"]
        Scalar(0.9, 1, na)
        '''
    @block.setter
    def block(self, value: str | list[str] | tuple[str | list[str], str]): ...
    @property
    def method(self) -> str:
        '''
        Estimation method.

        Parameters
        ----------
        value: EqMethod or str
            Possible values are LSQ, ZELLNER, INSTRUMENTAL, GLS, MAX_LIKELIHOOD.
        
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, EqMethod
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        
        >>> estimation.method
        \'LSQ\'
        >>> estimation.method = EqMethod.ZELLNER
        >>> estimation.method
        \'ZELLNER\'
        >>> estimation.method = "MAX_LIKELIHOOD"
        >>> estimation.method
        \'MAX_LIKELIHOOD\'
        '''
    @method.setter
    def method(self, value: EqMethod | str | int): ...
    @property
    def instruments(self) -> str | list[str]:
        '''
        Instrument(s) used for the estimation.

        Parameters
        ----------
        value: str or list(str)
            If several instruments are required for the estimation, they can be passed either as 
            a unique string in which instruments are separated by a semi colon \';\' or as a list of 
            strings.

        Notes
        -----
        Equivalent to the ODE_blk_instr() function of o_est.c from the old GUI (developed by Jean-Marc Paul)
        
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.instruments
        \'\'

        >>> # one instrument
        >>> estimation.instruments = "one_instrument"
        >>> estimation.instruments
        \'one_instrument\'

        >>> # several instruments
        >>> estimation.instruments = "several;instruments;as;unique;string"
        >>> estimation.instruments
        [\'several\', \'instruments\', \'as\', \'unique\', \'string\']
        >>> estimation.instruments = ["several", "instruments", "as", "list"]
        >>> estimation.instruments
        [\'several\', \'instruments\', \'as\', \'list\']
        '''
    @instruments.setter
    def instruments(self, value: str | list[str]): ...
    def update_scalars(self) -> None:
        """
        Update the local estimation Scalars database 'kdb_scl'.
        
        What the C++ method update_scalars() does:

            - Step 1: for each equation in the local estimation Equations database, get the list if corresponding scalars
            - Step 2: remove duplicated scalar names
            - Step 3: for each scalar name, check if it is already present in the local database 'kdb_scl':
\t                  - no  -> check if in the global Scalars database
                               - yes -> copy scalars from the global database to 'kdb_scl'. 
\t                           - no  -> add a new scalar with value = 0.0 and relax = 1.0 to 'kdb_scl'.
\t                  - yes -> does nothing.
            - Step 4: remove the scalars associated with equations which are not in the present block to estimate
        
        See :meth:`EditAndEstimateEquations.estimate` for the examples.

        Notes
        -----
        Equivalent to the ODE_blk_coef() function from o_est.c from the old GUI (developed by Jean-Marc Paul)
        """
    @property
    def scalars_db(self) -> Scalars:
        '''
        Local estimation Scalars database.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'

        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'DPUH\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\']
        
        >>> # ---- scalars list ----
        >>> estimation.update_scalars()
        >>> scalars_res = estimation.scalars_db
        >>> scalars_res.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        '''
    @property
    def equations_list(self) -> list[str]: ...
    @property
    def equations_db(self) -> Equations:
        '''
        Local estimation Equations database.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'

        >>> # ---- equations list ----
        >>> estimation.equations_list
        [\'ACAF\', \'DPUH\']
        >>> equations_res = estimation.equations_db
        >>> equations_res.names
        [\'ACAF\', \'DPUH\']
        '''
    def update_current_equation(self, lec: str, comment: str):
        """
        Update the LEC and comment of the current equation
        
        Notes
        -----
        Equivalent to the ODE_blk_save_cur() function from o_est.c from the old GUI (developed by Jean-Marc Paul)
        """
    @property
    def current_equation(self) -> Equation:
        '''
        Return the currently displayed equation in the GUI.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'

        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'ACAF\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\' 

        >>> # ---- next equation ---- 
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'DPUH\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'dln (DPUH/DPUHO):=dpuh_1+dpuh_2*dln(IHU/PI5)+dln PC\'

        >>> # ---- go back to first eq ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'ACAF\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'
        '''
    @property
    def next_equation(self) -> Equation:
        '''
        Move the equations iterator to the next one of the block if any or to the  
        first equation if the iterator was pointing to the last equation of the block.
        Then return the newly displayed equation.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'

        >>> # ---- current equation ----
        >>> current_eq = estimation.current_equation
        >>> current_eq.endogenous
        \'ACAF\'
        >>> current_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\' 

        >>> # ---- next equation ---- 
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'DPUH\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'dln (DPUH/DPUHO):=dpuh_1+dpuh_2*dln(IHU/PI5)+dln PC\'
        
        >>> # ---- go back to first eq ----
        >>> next_eq = estimation.next_equation
        >>> next_eq.endogenous
        \'ACAF\'
        >>> next_eq.lec           # doctest: +NORMALIZE_WHITESPACE
        \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\'
        '''
    @property
    def correlation_matrix(self) -> CorrelationMatrix:
        '''
        Coefficients correlation matrix.
        
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Equation
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations.clear()
        >>> scalars.clear()

        >>> equations["ACAF"] = Equation("ACAF", "(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> equations["DPUH"] = Equation("DPUH", "dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> success = estimation.estimate()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 2.01246)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 7.77305e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>

        >>> corr_matrix = estimation.correlation_matrix
        >>> corr_matrix.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> corr_matrix.shape
        (5, 5)
        >>> corr_matrix         # doctest: +NORMALIZE_WHITESPACE
                   |      acaf1       acaf2       acaf4      dpuh_1      dpuh_2
        ------------------------------------------------------------------------
             acaf1 |          1   -0.935266    0.200167   0.0448324  -0.0372903
             acaf2 |  -0.935266           1   -0.300833  -0.0016619   0.0395814
             acaf4 |   0.200167   -0.300833           1  0.00037477  -0.00892588
            dpuh_1 |  0.0448324  -0.0016619  0.00037477           1  -0.0419869
            dpuh_2 | -0.0372903   0.0395814  -0.00892588  -0.0419869           1
        <BLANKLINE>
        '''
    def get_observed_values(self, name: str) -> list[float]:
        '''
        Observed values (saved as the Variable `_YOBS`).

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Equation
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations.clear()
        >>> scalars.clear()

        >>> equations["ACAF"] = Equation("ACAF", "(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> equations["DPUH"] = Equation("DPUH", "dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> success = estimation.estimate()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 2.01246)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 7.77305e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>

        >>> estimation.get_observed_values("ACAF")      # doctest: +ELLIPSIS
        [0.011412041862997465, 0.016028202180810566, ..., -0.002985052229901132, 0.00695696806902914]
        >>> estimation.get_fitted_values("ACAF")        # doctest: +ELLIPSIS
        [0.01256212379902573, 0.01249107519078254, ..., -0.0029850522299011313, 0.004490336374472825]
        >>> estimation.get_residual_values("ACAF")      # doctest: +ELLIPSIS
        [-0.001150081936028266, 0.0035371269900280264, ..., -8.673617379884035e-19, 0.0024666316945563148]

        >>> estimation.get_observed_values("DPUH")      # doctest: +ELLIPSIS
        [0.06044527980207867, 0.08768972383253629, ..., 0.0424313077256923, 0.0064336499579307135]
        >>> estimation.get_fitted_values("DPUH")        # doctest: +ELLIPSIS
        [0.07361898875461417, 0.0642394908832952, ..., 0.028792670295107632, 0.032048802201317866]
        >>> estimation.get_residual_values("DPUH")      # doctest: +ELLIPSIS
        [-0.013173708952535501, 0.02345023294924109, ..., 0.013638637430584667, -0.025615152243387153]
        '''
    def get_fitted_values(self, name: str) -> list[float]:
        '''
        Fitted values for estimation (saved as the Variable `_CALC`)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Equation
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations.clear()
        >>> scalars.clear()

        >>> equations["ACAF"] = Equation("ACAF", "(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> equations["DPUH"] = Equation("DPUH", "dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> success = estimation.estimate()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 2.01246)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 7.77305e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>

        >>> estimation.get_observed_values("ACAF")      # doctest: +ELLIPSIS
        [0.011412041862997465, 0.016028202180810566, ..., -0.002985052229901132, 0.00695696806902914]
        >>> estimation.get_fitted_values("ACAF")        # doctest: +ELLIPSIS
        [0.01256212379902573, 0.01249107519078254, ..., -0.0029850522299011313, 0.004490336374472825]
        >>> estimation.get_residual_values("ACAF")      # doctest: +ELLIPSIS
        [-0.001150081936028266, 0.0035371269900280264, ..., -8.673617379884035e-19, 0.0024666316945563148]

        >>> estimation.get_observed_values("DPUH")      # doctest: +ELLIPSIS
        [0.06044527980207867, 0.08768972383253629, ..., 0.0424313077256923, 0.0064336499579307135]
        >>> estimation.get_fitted_values("DPUH")        # doctest: +ELLIPSIS
        [0.07361898875461417, 0.0642394908832952, ..., 0.028792670295107632, 0.032048802201317866]
        >>> estimation.get_residual_values("DPUH")      # doctest: +ELLIPSIS
        [-0.013173708952535501, 0.02345023294924109, ..., 0.013638637430584667, -0.025615152243387153]
        '''
    def get_residual_values(self, name: str) -> list[float]:
        '''
        Difference between the observations and the estimate values (saved as the Variable `YRES`).

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Equation
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations.clear()
        >>> scalars.clear()

        >>> equations["ACAF"] = Equation("ACAF", "(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> equations["DPUH"] = Equation("DPUH", "dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> success = estimation.estimate()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 2.01246)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 7.77305e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>

        >>> estimation.get_observed_values("ACAF")      # doctest: +ELLIPSIS
        [0.011412041862997465, 0.016028202180810566, ..., -0.002985052229901132, 0.00695696806902914]
        >>> estimation.get_fitted_values("ACAF")        # doctest: +ELLIPSIS
        [0.01256212379902573, 0.01249107519078254, ..., -0.0029850522299011313, 0.004490336374472825]
        >>> estimation.get_residual_values("ACAF")      # doctest: +ELLIPSIS
        [-0.001150081936028266, 0.0035371269900280264, ..., -8.673617379884035e-19, 0.0024666316945563148]

        >>> estimation.get_observed_values("DPUH")      # doctest: +ELLIPSIS
        [0.06044527980207867, 0.08768972383253629, ..., 0.0424313077256923, 0.0064336499579307135]
        >>> estimation.get_fitted_values("DPUH")        # doctest: +ELLIPSIS
        [0.07361898875461417, 0.0642394908832952, ..., 0.028792670295107632, 0.032048802201317866]
        >>> estimation.get_residual_values("DPUH")      # doctest: +ELLIPSIS
        [-0.013173708952535501, 0.02345023294924109, ..., 0.013638637430584667, -0.025615152243387153]
        '''
    def estimate(self, maxit: int = 100, epsilon: float = 1e-06, quiet: bool = False) -> bool:
        '''
        Estimate the current block of equations (which is not necessarily all the equations 
        in the local Equations database \'kdb_eqs\').

        Parameters
        ----------
        maxit: int, optional
            Maximum number of iterations for the estimation. 
            Default is 100.
        epsilon: float, optional
            Convergence criterion for the estimation. 
            Default is 1.0e-6.
        quiet: bool, optional
            If True, the estimation will be silent (no printout). 
            Default is False.

        Returns
        -------
        True if the estimation was successful, False otherwise.

        Notes
        -----
        Equivalent to ODE_blk_est() from o_est.c from the old GUI (developed by Jean-Marc Paul).

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Equation
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations.clear()
        >>> scalars.clear()

        >>> equations["ACAF"] = Equation("ACAF", "(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> equations["DPUH"] = Equation("DPUH", "dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)")

        >>> from iode.compute.estimation import EditAndEstimateEquations
        >>> estimation = EditAndEstimateEquations("1980Y1", "1996Y1")
        >>> estimation.block = "ACAF;DPUH", "ACAF"
        >>> estimation.block
        \'ACAF;DPUH\'

        >>> scalars_est = estimation.scalars_db
        >>> scalars_est.names
        []
        >>> estimation.update_scalars()
        >>> scalars_est.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> scalars_est["acaf1"]
        Scalar(0.9, 1, na)
        >>> scalars_est["dpuh_1"]
        Scalar(0.9, 1, na)

        >>> equations_est = estimation.equations_db
        >>> equations_est["ACAF"]               # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                 lec = \'(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')
        >>> equations_est["DPUH"]               # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'DPUH\',
                 lec = \'dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')

        >>> estimation.is_done
        False
        >>> success = estimation.estimate()                 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 2.01246)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 7.77305e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        >>> estimation.is_done
        True

        >>> scalars_est["acaf1"]
        Scalar(0.0157705, 1, 0.00136079)
        >>> scalars_est["dpuh_1"]
        Scalar(0.0109855, 1, 0.00481857)

        >>> corr_matrix = estimation.correlation_matrix
        >>> corr_matrix.names
        [\'acaf1\', \'acaf2\', \'acaf4\', \'dpuh_1\', \'dpuh_2\']
        >>> corr_matrix.shape
        (5, 5)
        >>> corr_matrix         # doctest: +NORMALIZE_WHITESPACE
                   |      acaf1       acaf2       acaf4      dpuh_1      dpuh_2
        ------------------------------------------------------------------------
             acaf1 |          1   -0.935266    0.200167   0.0448324  -0.0372903
             acaf2 |  -0.935266           1   -0.300833  -0.0016619   0.0395814
             acaf4 |   0.200167   -0.300833           1  0.00037477  -0.00892588
            dpuh_1 |  0.0448324  -0.0016619  0.00037477           1  -0.0419869
            dpuh_2 | -0.0372903   0.0395814  -0.00892588  -0.0419869           1
        <BLANKLINE>

        >>> equations_est["ACAF"]             # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF;DPUH\',
                tests = {corr = 1,
                         dw = 2.33007,
                         fstat = 32.2851,
                         loglik = 83.8101,
                         meany = 0.00818467,
                         r2 = 0.821815,
                         r2adj = 0.79636,
                         ssres = 5.19787e-05,
                         stderr = 0.00192685,
                         stderrp = 23.5422,
                         stdev = 0.0042699},
                date = ...)
        >>> equations_est["DPUH"]             # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
        Equation(endogenous = \'DPUH\',
                lec = \'dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF;DPUH\',
                tests = {corr = 0.126096,
                         dw = 3.15593,
                         fstat = 3.51611,
                         loglik = 43.5743,
                         meany = 0.0505132,
                         r2 = 0.189895,
                         r2adj = 0.135888,
                         ssres = 0.00591031,
                         stderr = 0.01985,
                         stderrp = 39.2966,
                         stdev = 0.0213538},
                date = ...)

        >>> # global Equations and Scalars databases are left intact by the method estimate()
        >>> equations["ACAF"]                   # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                 lec = \'(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')
        >>> equations["DPUH"]                   # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'DPUH\',
                 lec = \'dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')
        >>> scalars["acaf1"]
        Scalar(0.9, 1, na)
        >>> scalars["dpuh_1"]
        Scalar(0.9, 1, na)

        >>> # save results in the global databases
        >>> new_eqs = estimation.save()
        >>> new_eqs
        []
        >>> equations["ACAF"]             # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                 lec = \'(ACAF/VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                 method = \'LSQ\',
                 from_period = \'1980Y1\',
                 to_period = \'1996Y1\',
                 block = \'ACAF;DPUH\',
                 tests = {corr = 1,
                          dw = 2.33007,
                          fstat = 32.2851,
                          loglik = 83.8101,
                          meany = 0.00818467,
                          r2 = 0.821815,
                          r2adj = 0.79636,
                          ssres = 5.19787e-05,
                          stderr = 0.00192685,
                          stderrp = 23.5422,
                          stdev = 0.0042699},
                 date = ...)
        >>> equations["DPUH"]             # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Equation(endogenous = \'DPUH\',
                 lec = \'dln(DPUH/DPUHO) := dpuh_1 + dpuh_2 * dln(IHU/PI5) + dln(PC)\',
                 method = \'LSQ\',
                 from_period = \'1980Y1\',
                 to_period = \'1996Y1\',
                 block = \'ACAF;DPUH\',
                 tests = {corr = 0.126096,
                          dw = 3.15593,
                          fstat = 3.51611,
                          loglik = 43.5743,
                          meany = 0.0505132,
                          r2 = 0.189895,
                          r2adj = 0.135888,
                          ssres = 0.00591031,
                          stderr = 0.01985,
                          stderrp = 39.2966,
                          stdev = 0.0213538},
                 date = ...)
        >>> scalars["acaf1"]
        Scalar(0.0157705, 1, 0.00136079)
        >>> scalars["dpuh_1"]
        Scalar(0.0109855, 1, 0.00481857)
        '''
    @property
    def is_done(self) -> bool: ...
    def save(self, from_period: str | list[str] = None, to_period: str | list[str] = None) -> list[str]:
        """
        - copy the equations referenced in the vector 'v_equations' from the local Equations database 
          to the global Equations database,
        - if estimation -> create/update the scalars containing the results of the estimated equation(s),
        - merge the local Scalars database into the global Scalars database,
        - return the list of names of the new equations.

        See :meth:`EditAndEstimateEquations.estimate` for the examples.
        
        Parameters
        ----------
        from_period: str or Period, optional
            Starting period to copy if no estimation has been done
        to_period: str or Period, optional
            Ending period to copy if no estimation has been done
        
        Returns
        -------
        list(str)
            List of the names of the new equations

        Notes
        -----
        Equivalent to the ODE_blk_save() function from o_est.c from the old GUI (developed by Jean-Marc Paul).
        """
