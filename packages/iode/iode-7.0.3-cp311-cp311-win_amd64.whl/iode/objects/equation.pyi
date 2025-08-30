from iode.common import EqMethod as EqMethod, EqTest as EqTest
from iode.time.period import Period as Period
from iode.time.sample import Sample as Sample
from iode.util import enable_msgs as enable_msgs, suppress_msgs as suppress_msgs
from typing import Any, Self

Self = Any

class Equation:
    '''
    An *equation* represents an equality mixing *variables* and *scalars* (coefficients) 
    and is part of a model. Each equation is composed of the following elements:

    - the *LEC* form (the formula scripting language in IODE)
    - a free comment (title of the equation)
    - the method by which it was estimated (if applicable)
    - the possible estimation period
    - the names of equations estimated simultaneously (block)
    - the instruments used for the estimation

    All these definition elements are present in each equation, but may be left empty 
    if not applicable.

    The name of an equation is that of its endogenous variable. 
    An equation can never be renamed, but it can be deleted and redefined with a new name.

    Attributes
    ----------
    endogenous: str
        name of the endogenous variable. It must the same as the name of the present 
        equation in the Equations database. 
    lec: str
        LEC expression of the equation.
    method: EqMethod
        estimation method. Possible values are:
            - LSQ
            - ZELLNER
            - INSTRUMENTAL
            - GLS
            - MAX_LIKELIHOOD
    sample: Sample
        estimaton sample.
    comment: str
    instruments: str
        estimation instruments.
    block: str
        block of equations (to estimate) to which the equation belong.
    tests: dict(str, float)
        tests values associated with the estimation of the equation.
    date: str
        last time the equation has been estimated.

    Parameters
    ----------
    endogenous: str
        Name of the endogenous variable. It must the same as the name of the present 
        equation in the Equations database. 
    lec: str
        LEC expression of the equation.
    method: EqMethod or str, optional
        Method used to estimate the coefficients of the equation.
        Defaults to LSQ.
    from_period: str or Period, optional
        Starting period for the estimation.
        Defaults to the starting period of the sample associated with the IODE Variables database.
    to_period: str or Period, optional
        Ending period for the estimation.
        Defaults to the ending period of the sample associated with the IODE Variables database.
    comment: str, optional
        Defaults to empty.
    instruments: str, optional
        Defaults to empty.
    block: str, optional
        block of equations (to estimate) to which the equation belong.
        Defaults to empty.

    Examples
    --------
    >>> from iode import Equation, variables
    >>> variables.sample = "1960Y1:2015Y1"
    >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
    >>> eq_ACAF         # doctest: +NORMALIZE_WHITESPACE
    Equation(endogenous = \'ACAF\',
             lec = \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
             method = \'LSQ\',
             from_period = \'1960Y1\',
             to_period = \'2015Y1\')
    '''
    def __init__(self, endogenous: str, lec: str, method: EqMethod | str = ..., from_period: str | Period = None, to_period: str | Period = None, comment: str = '', instruments: str = '', block: str = '') -> None: ...
    @classmethod
    def get_instance(cls) -> Self: ...
    def get_formated_date(self, format: str = 'dd-mm-yyyy') -> str:
        '''
        Return the date of last estimation in a given format.

        Returns
        -------
        str

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> # date as default format "dd-mm-yyyy"
        >>> equations["ACAF"].date
        \'12-06-1998\'
        >>> # date with specific format
        >>> equations["ACAF"].get_formated_date("dd/mm/yyyy")
        \'12/06/1998\'
        '''
    @property
    def coefficients(self) -> list[str]:
        '''
        Return the list of coefficients present in the current equation.

        Returns
        -------
        list(str)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR
        >>> from iode import Equation, scalars, variables
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")      # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")    # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> eq_ACAF         # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                 lec = \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')
        >>> eq_ACAF.coefficients
        [\'acaf1\', \'acaf2\', \'acaf4\']
        '''
    @property
    def variables(self) -> list[str]:
        '''
        Return the list of variables present in the equation.

        Returns
        -------
        list(str)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR
        >>> from iode import Equation, scalars, variables
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> eq_ACAF         # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                 lec = \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                 method = \'LSQ\',
                 from_period = \'1960Y1\',
                 to_period = \'2015Y1\')
        >>> eq_ACAF.variables
        [\'ACAF\', \'VAF\', \'GOSF\', \'TIME\']
        '''
    def split_equation(self) -> tuple[str, str]:
        '''
        Split an equation into its left-hand side and its right-hand side.

        Returns
        -------
        tuple(str, str)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR
        >>> from iode import Equation
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> lhs, rhs = eq_ACAF.split_equation()
        >>> # left-hand side
        >>> lhs
        \'(ACAF / VAF[-1])\'
        >>> # right-hand side
        >>> rhs
        \'acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\'
        '''
    def estimate(self, from_period: str | Period = None, to_period: str | Period = None, maxit: int = 100, epsilon: float = 1e-06, quiet: bool = False) -> bool:
        '''
        Estimate the present equation.

        At the end of the estimation process, certain variables and scalars are automatically created 
        if the process has converged. These variables and scalars can be used for computational purposes and, 
        as they are part of the global workspace, can be saved for future use.

        The tests resulting from the last estimation are saved as scalars. The same applies to residuals, 
        left-hand and right-hand members of equations.

        Saved tests (as scalars) have the following names:

            - `e0_n` : number of sample periods 
            - `e0_k` : number of estimated coefficients 
            - `e0_stdev` : std dev of residuals 
            - `e0_meany` : mean of Y 
            - `e0_ssres` : sum of squares of residuals 
            - `e0_stderr` : std error 
            - `e0_stderrp` : std error percent (in %) 
            - `e0_fstat` : F-Stat 
            - `e0_r2` : R square 
            - `e0_r2adj` : adjusted R-squared 
            - `e0_dw` : Durbin-Watson 
            - `e0_loglik` : Log Likelihood 

        Calculated series are saved in special variables:

            - `_YCALC0` : right-hand side of the equation
            - `_YOBS0` : left-hand side of the equation
            - `_YRES0` : residuals of the equation

        Outside the estimation sample, the series values are :math:`NA`.

        Parameters
        ----------
        from_period : str or Period, optional
            The starting period of the execution range. 
            Defaults to the starting period of the current Variables sample.
        to_period : str or Period, optional
            The ending period of the execution range.
            Defaults to the ending period of the current Variables sample.
        maxit : int, optional
            The maximum number of iterations for the estimation process.
            Defaults to 100.
        epsilon : float, optional
            The convergence threshold for the estimation process.
            Defaults to 1.0e-6.
        quiet : bool, optional
            If True, suppresses the log messages during the estimation process. 
            Default to False.

        Returns
        -------
        bool
            True if the estimation process has converged, False otherwise.

        Warnings
        --------
        If the present equation belongs to a block, you must use the :meth:`Equations.estimate` method instead.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded

        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> eq_ACAF.lec
        \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\'

        >>> # create scalars
        >>> scalars["acaf1"] = 0., 1.
        >>> scalars["acaf2"] = 0., 1.
        >>> scalars["acaf4"] = 0., 1.

        >>> # estimate the ACAF equation
        >>> success = eq_ACAF.estimate("1980Y1", "2000Y1") 
        Estimating : iteration 1 (||eps|| = 0.173205)
        Estimating : iteration 2 (||eps|| = 9.24137e-09)
        Solution reached after 2 iteration(s). Creating results file ...
        >>> success
        True
        >>> scalars["acaf1"]
        Scalar(0.0150646, 1, 0.00118455)
        >>> scalars["acaf2"]
        Scalar(-6.90855e-06, 1, 1.07873e-06)
        >>> scalars["acaf4"]
        Scalar(-0.00915675, 1, 0.00209541)
        >>> eq_ACAF                             # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'2000Y1\',
                tests = {corr = 1,
                         dw = 1.87449,
                         fstat = 34.6629,
                         loglik = 102.07,
                         meany = 0.0075289,
                         r2 = 0.793875,
                         r2adj = 0.770973,
                         ssres = 7.37883e-05,
                         stderr = 0.00202468,
                         stderrp = 26.8922,
                         stdev = 0.00423072},
                date = \'...\')
        >>> # observed values (left hand side of the equation)
        >>> variables["_YOBS0", "1980Y1:2000Y1"]        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Workspace: Variables
        nb variables: 1
        filename: ...fun.var
        description: Modèle fun - Simulation 1
        sample: 1980Y1:2000Y1
        mode: LEVEL
        <BLANKLINE>
         name      1980Y1  1981Y1  1982Y1  ...  1998Y1  1999Y1  2000Y1
        _YOBS0       0.01    0.02    0.01  ...    0.01    0.00    0.00
        <BLANKLINE>
        >>> # fitted values (right hand side of the equation)
        >>> variables["_YCALC0", "1980Y1:2000Y1"]       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Workspace: Variables
        nb variables: 1
        filename: ...fun.var
        description: Modèle fun - Simulation 1
        sample: 1980Y1:2000Y1
        mode: LEVEL
        <BLANKLINE>
          name     1980Y1  1981Y1  1982Y1  ...  1998Y1  1999Y1  2000Y1
        _YCALC0      0.01    0.01    0.01  ...    0.00    0.00    0.00
        <BLANKLINE>
        >>> # residuals values
        >>> variables["_YRES0", "1980Y1:2000Y1"]        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Workspace: Variables
        nb variables: 1
        filename: ...fun.var
        description: Modèle fun - Simulation 1
        sample: 1980Y1:2000Y1
        mode: LEVEL
        <BLANKLINE>
         name      1980Y1  1981Y1  1982Y1  ...  1998Y1  1999Y1  2000Y1
        _YRES0      -0.00    0.00   -0.00  ...    0.00   -0.00   -0.00
        <BLANKLINE>
        '''
    def estimate_step_wise(self, from_period: str | Period = None, to_period: str | Period = None, lec_condition: str = None, test: str = 'r2') -> bool:
        '''
        Estimates an equation and searches for the best possible test values for all 
        possible combinations of coefficients.

        Parameters
        ----------
        from_period : str, optional
            The starting period for the estimation.
            Defaults to the starting period of the current Variables sample.
        to_period : str, optional
            The ending period for the estimation.
            Defaults to the ending period of the current Variables sample.
        lec_condition : str
            Boolean condition written as a LEC expression which is evaluated for each 
            combination of coefficients. Defaults to None (no condition).
        test : str, {r2|fstat}
            Test name. It must be either \'r2\' or \'fstat\'.
            Defaults to \'r2\'.

        Returns
        -------
        bool
            True if the estimation process has converged, False otherwise.
            
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, scalars, variables, Scalar
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded
        >>> scalars.load(f"{SAMPLE_DATA_DIR}/fun.scl")          # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.scl
        161 objects loaded
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> coefficient_names = eq_ACAF.coefficients
        >>> coefficient_names
        [\'acaf1\', \'acaf2\', \'acaf4\']

        Estimate the equation for the test \'r2\' with no condition

        >>> # reset the coefficients
        >>> scalars[coefficient_names] = Scalar(0.9, 1.)
        >>> # estimate 
        >>> success = eq_ACAF.estimate_step_wise("1980Y1", "2000Y1")      # doctest: +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 2.4346e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 , r2=0.575200
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 1.75111e-10)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf4 , r2=0.324238
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , r2=-1.058215
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , r2=0.793875
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , r2=0.793875
        >>> success
        True
        >>> # r2
        >>> eq_ACAF.tests["r2"]
        0.7938754558563232
        >>> # display the estimated coefficients
        >>> for name in coefficient_names:
        ...     print(f"{name} -> {scalars[name]}")
        acaf1 -> Scalar(0.0150646, 1, 0.00118455)
        acaf2 -> Scalar(-6.90855e-06, 1, 1.07873e-06)
        acaf4 -> Scalar(-0.00915675, 1, 0.00209541)

        Estimate the equation for the test \'fstat\' with no condition

        >>> # reset the coefficients
        >>> scalars[coefficient_names] = Scalar(0.9, 1.)
        >>> # estimate 
        >>> success = eq_ACAF.estimate_step_wise("1980Y1", "2000Y1", test="fstat")        # doctest: +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 2.4346e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 , fstat=25.726931
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 1.75111e-10)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf4 , fstat=9.116395
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , fstat=-9.768702
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , fstat=34.662926
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , fstat=34.662926
        >>> success
        True
        >>> # fstat
        >>> eq_ACAF.tests["fstat"]
        34.662925720214844
        >>> # display the estimated coefficients
        >>> for name in coefficient_names:
        ...     print(f"{name} -> {scalars[name]}")
        acaf1 -> Scalar(0.0150646, 1, 0.00118455)
        acaf2 -> Scalar(-6.90855e-06, 1, 1.07873e-06)
        acaf4 -> Scalar(-0.00915675, 1, 0.00209541)

        Estimate the equation for the test \'r2\' with condition (acaf2 > 0)

        >>> # write the condition (all coefficients > 0)
        >>> lec_condition = "acaf2 > 0"
        >>> lec_condition
        \'acaf2 > 0\'
        >>> # reset the coefficients
        >>> scalars[coefficient_names] = Scalar(0.9, 1.)
        >>> # estimate 
        >>> success = eq_ACAF.estimate_step_wise("1980Y1", "2000Y1", lec_condition)       # doctest: +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 2.4346e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 , r2=0.575200
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 1.75111e-10)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf4 , r2=0.324238
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , r2=-1.058215
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , r2=0.793875
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , r2=-1.058215
        >>> success
        True
        >>> # r2
        >>> eq_ACAF.tests["r2"]
        -1.0582152605056763
        >>> # display the estimated coefficients
        >>> for name in coefficient_names:
        ...     print(f"{name} -> {scalars[name]}")
        acaf1 -> Scalar(0, 0, 0)
        acaf2 -> Scalar(5.76933e-06, 1, 1.26806e-06)
        acaf4 -> Scalar(-0.0104115, 1, 0.00643766)

        Estimate the equation for the test \'fstat\' with condition (acaf2 > 0)

        >>> # reset the coefficients
        >>> scalars[coefficient_names] = Scalar(0.9, 1.)
        >>> # estimate 
        >>> success = eq_ACAF.estimate_step_wise("1980Y1", "2000Y1", lec_condition, "fstat")      # doctest: +NORMALIZE_WHITESPACE
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 2.4346e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 , fstat=25.726931
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 1.75111e-10)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf4 , fstat=9.116395
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , fstat=-9.768702
        Estimating : iteration 1 (||eps|| = 1.55885)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 5.30092e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf1 acaf2 acaf4 , fstat=34.662926
        Estimating : iteration 1 (||eps|| = 1.27279)
        <BLANKLINE>
        Estimating : iteration 2 (||eps|| = 4.13603e-08)
        <BLANKLINE>
        Solution reached after 2 iteration(s). Creating results file ...
        <BLANKLINE>
        ACAF: scalars : acaf2 acaf4 , fstat=-9.768702
        >>> success
        True
        >>> # fstat
        >>> eq_ACAF.tests["fstat"]
        -9.768701553344727
        >>> # display the estimated coefficients
        >>> for name in coefficient_names:
        ...     print(f"{name} -> {scalars[name]}")
        acaf1 -> Scalar(0, 0, 0)
        acaf2 -> Scalar(5.76933e-06, 1, 1.26806e-06)
        acaf4 -> Scalar(-0.0104115, 1, 0.00643766)
        '''
    @property
    def endogenous(self) -> str: ...
    @property
    def lec(self) -> str:
        '''
        LEC expression of the current equation.

        Paramaters
        ----------
        value: str
            New LEC expression.

        Examples
        --------
        >>> from iode import Equation
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> eq_ACAF.endogenous
        \'ACAF\'
        >>> eq_ACAF.lec
        \'(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\'
        >>> # remove acaf1 from the LEC expression of the ACAF equation
        >>> eq_ACAF.lec = "(ACAF / VAF[-1]) := acaf2 * GOSF[-1] + acaf4 * (TIME=1995)"
        >>> eq_ACAF.lec
        \'(ACAF / VAF[-1]) := acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\'
        >>> # wrong name for the endogenous variable
        >>> eq_ACAF.lec = "(ACAF_ / VAF[-1]) := acaf2 * GOSF[-1] + acaf4 * (TIME=1995)"
        Traceback (most recent call last):
        ... 
        ValueError: Cannot set LEC \'(ACAF_ / VAF[-1]) := acaf2 * GOSF[-1] + acaf4 * (TIME=1995)\' to the equation named \'ACAF\'
        '''
    @lec.setter
    def lec(self, value: str): ...
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
        >>> from iode import Equation, EqMethod
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> # default value
        >>> eq_ACAF.method
        \'LSQ\'
        >>> eq_ACAF.method = EqMethod.GLS
        >>> eq_ACAF.method
        \'GLS\'
        >>> eq_ACAF.method = \'MAX_LIKELIHOOD\'
        >>> eq_ACAF.method
        \'MAX_LIKELIHOOD\'
        '''
    @method.setter
    def method(self, value: EqMethod | str): ...
    @property
    def sample(self) -> Sample:
        '''
        Estimation sample of the current equation.

        Parameters
        ----------
        value: str or Sample
            New estimation sample

        Examples
        --------
        >>> from iode import Equation, variables
        >>> variables.clear()
        >>> variables.sample
        None
        >>> eq_ACAF = Equation("ACAF", "(ACAF / VAF[-1]) := acaf1 + acaf2 * GOSF[-1] + acaf4 * (TIME=1995)")
        >>> eq_ACAF.sample
        None

        >>> # set Variables sample
        >>> variables.sample = "1960Y1:2015Y1"
        >>> variables.sample
        Sample("1960Y1:2015Y1")

        >>> # specify starting and ending periods
        >>> eq_ACAF.sample = "1980Y1:2000Y1"
        >>> eq_ACAF.sample
        Sample("1980Y1:2000Y1")

        >>> # specify only the starting period 
        >>> # -> ending period = ending period of the Variables sample
        >>> eq_ACAF.sample = "1990Y1:"
        >>> eq_ACAF.sample
        Sample("1990Y1:2015Y1")

        >>> # specify only the ending period 
        >>> # -> starting period = starting period of the Variables sample
        >>> eq_ACAF.sample = ":2010Y1"
        >>> eq_ACAF.sample
        Sample("1960Y1:2010Y1")

        >>> # specify nothing
        >>> # new equation sample = Variables sample
        >>> eq_ACAF.sample = ":"
        >>> eq_ACAF.sample
        Sample("1960Y1:2015Y1")
        '''
    @sample.setter
    def sample(self, value: str | Sample): ...
    @property
    def comment(self) -> str:
        """
        Equation comment.
        """
    @comment.setter
    def comment(self, value: str): ...
    @property
    def instruments(self) -> str | list[str]:
        """
        Instrument(s) used for the estimation.

        Parameters
        ----------
        value: str or list(str)
            If several instruments are required for the estimation, they can be passed either as 
            a unique string in which instruments are separated by a semi colon ';' or as a list of 
            strings.
        """
    @instruments.setter
    def instruments(self, value: str | list[str]): ...
    @property
    def block(self) -> str:
        '''
        Estimation block of equations to which the equation belongs.

        Parameters
        ----------
        value: str or list(str)
           
        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> equations["ACAF"].block             # doctest: +NORMALIZE_WHITESPACE
        \'ACAF\'
        '''
    @block.setter
    def block(self, value: str | list[str]): ...
    @property
    def tests(self) -> dict[str, float]:
        '''
        Estimation tests.

        Returns
        -------
        dict(str, float)

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> equations["ACAF"].tests             # doctest: +NORMALIZE_WHITESPACE
        {\'corr\': 1.0, \'dw\': 2.329345941543579, \'fstat\': 32.273193359375, \'loglik\': 83.80752563476562, 
        \'meany\': 0.008184665814042091, \'r2\': 0.8217613697052002, \'r2adj\': 0.7962986826896667, 
        \'ssres\': 5.1994487876072526e-05, \'stderr\': 0.0019271461060270667, \'stderrp\': 23.545812606811523, 
        \'stdev\': 0.004269900266081095}
        '''
    @property
    def date(self) -> str:
        '''
        Date of the last estimation.
        
        Returns
        -------
        str

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")       # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> equations["ACAF"].date
        \'12-06-1998\'
        '''
    def copy(self) -> Self:
        '''
        Return a copy of the current Equation.

        Examples
        --------
        >>> from iode import SAMPLE_DATA_DIR, equations, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations["ACAF"]           # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF\',
                tests = {corr = 1,
                         dw = 2.32935,
                         fstat = 32.2732,
                         loglik = 83.8075,
                         meany = 0.00818467,
                         r2 = 0.821761,
                         r2adj = 0.796299,
                         ssres = 5.19945e-05,
                         stderr = 0.00192715,
                         stderrp = 23.5458,
                         stdev = 0.0042699},
                date = \'12-06-1998\')
        >>> copied_eq = equations["ACAF"].copy()
        >>> copied_eq                   # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF\',
                tests = {corr = 1,
                         dw = 2.32935,
                         fstat = 32.2732,
                         loglik = 83.8075,
                         meany = 0.00818467,
                         r2 = 0.821761,
                         r2adj = 0.796299,
                         ssres = 5.19945e-05,
                         stderr = 0.00192715,
                         stderrp = 23.5458,
                         stdev = 0.0042699},
                date = \'12-06-1998\')
        '''
    def __eq__(self, other: Self) -> bool: ...
    def __copy__(self) -> Self:
        '''
        Return a copy of the current Equation.

        Examples
        --------
        >>> from copy import copy
        >>> from iode import SAMPLE_DATA_DIR, equations, variables
        >>> equations.load(f"{SAMPLE_DATA_DIR}/fun.eqs")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.eqs
        274 objects loaded 
        >>> variables.load(f"{SAMPLE_DATA_DIR}/fun.var")        # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Loading .../fun.var
        394 objects loaded
        >>> equations["ACAF"]           # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF\',
                tests = {corr = 1,
                         dw = 2.32935,
                         fstat = 32.2732,
                         loglik = 83.8075,
                         meany = 0.00818467,
                         r2 = 0.821761,
                         r2adj = 0.796299,
                         ssres = 5.19945e-05,
                         stderr = 0.00192715,
                         stderrp = 23.5458,
                         stdev = 0.0042699},
                date = \'12-06-1998\')
        >>> copied_eq = copy(equations["ACAF"])
        >>> copied_eq                   # doctest: +NORMALIZE_WHITESPACE
        Equation(endogenous = \'ACAF\',
                lec = \'(ACAF/VAF[-1]) :=acaf1+acaf2*GOSF[-1]+\\nacaf4*(TIME=1995)\',
                method = \'LSQ\',
                from_period = \'1980Y1\',
                to_period = \'1996Y1\',
                block = \'ACAF\',
                tests = {corr = 1,
                         dw = 2.32935,
                         fstat = 32.2732,
                         loglik = 83.8075,
                         meany = 0.00818467,
                         r2 = 0.821761,
                         r2adj = 0.796299,
                         ssres = 5.19945e-05,
                         stderr = 0.00192715,
                         stderrp = 23.5458,
                         stdev = 0.0042699},
                date = \'12-06-1998\')
        '''
    def __hash__(self) -> int: ...
