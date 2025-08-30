from iode.common import PeriodICITY_LIST as PeriodICITY_LIST
from typing import Any, Self

Self = Any

class Period:
    def __init__(self, period_or_year: str | int | Self, periodicity: str = 'Y', step: int = 1) -> None:
        '''
        An IODE period is defined by a year, a periodicity and by a position in the year.

        Possible values for the periodicity are:

            - Y: yearly
            - S: semestrial
            - Q: quarterly
            - M: monthly
            - W: weekly
            - D: daily

        Parameters
        ----------
        period_or_year: str or int
            If str, it is consided as a string representing the year, the periodicity 
            and the position of the period in the year (step).
            If int, it is considered as the year of the period.
        periodicity: str, optional
                Periodicity of the period. Possible values are \'Y\', \'S\', \'Q\', \'M\', \'W\' and \'D\'.
                Default to \'Y\' (yearly).
        step: int, optional
                Position of the period in the year. 
                Default to 1.

        Attributes
        ----------
        year: int
        periodicity: str
        step: int
            position in the year

        Examples
        --------
        >>> from iode import Period
        >>> # passing a string
        >>> period = Period("2000Y1")
        >>> period
        Period("2000Y1")
        >>> # passing year, periodicity and step
        >>> period = Period(2010, \'Q\', 1)
        >>> period
        Period("2010Q1")
        >>> # passing only year
        >>> period = Period(2010)
        >>> period
        Period("2010Y1")
        >>> # passing year and periodicity
        >>> period = Period(2010, \'Q\')
        >>> period
        Period("2010Q1")
        >>> # copy a period
        >>> period_2 = Period(period)
        >>> period_2
        Period("2010Q1")
        '''
    @classmethod
    def get_instance(cls) -> Self: ...
    @property
    def nb_periods_per_year(self) -> int:
        """
        Number of periods in a year according to the periodicity.

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2010, 'Q', 1)
        >>> period.nb_periods_per_year
        4
        """
    def difference(self, other: Self) -> int:
        """
        Number of sub periods between two periods. 
        The two periods must have the same periodicity.

        Parameters
        ----------
        other: Period

        Returns
        -------
        int

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, 'Q', 1)
        >>> period_2 = Period(2001, 'Q', 3)
        >>> period.difference(period_2)
        -6
        >>> period_2.difference(period)
        6
        """
    def shift(self, nb_periods: int) -> Self:
        '''
        Shift the current period by a number of sub periods.
        If the number of sub periods is positive, the shift is time forward.  
        Conversely, if the number of sub periods is negative, the shift is time backward.  

        Parameters
        ----------
        nb_periods: int
            Number of sub periods. 
            The shift is time forward if positive and time backward if negative. 

        Returns
        -------
        shifted_period: Period

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, \'Q\', 1)
        >>> period
        Period("2000Q1")
        >>> # shift forward
        >>> shifted_period = period.shift(7)
        >>> shifted_period
        Period("2001Q4")
        >>> # shift backward
        >>> shifted_period = period.shift(-7)
        >>> shifted_period
        Period("1998Q2")
        '''
    @property
    def year(self) -> int:
        """
        Corresponding year of the period

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, 'Q', 3)
        >>> period.year
        2000
        """
    @property
    def periodicity(self) -> str:
        """
        Possible values are:

            - Y: yearly
            - S: semestrial
            - Q: quarterly
            - M: monthly
            - W: weekly
            - D: daily
        
        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, 'Q', 3)
        >>> period.periodicity
        'Q'
        """
    @property
    def step(self) -> int:
        """
        Position of the period in the year

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, 'Q', 3)
        >>> period.step
        3
        """
    def __eq__(self, other: Self) -> bool: ...
    def __float__(self) -> float:
        """
        Returns a float representation of the period.

        Returns
        -------
        float

        Examples
        --------
        >>> from iode import Period
        >>> period = Period(2000, 'Q', 1)
        >>> float(period)
        2000.0
        >>> period = Period(2000, 'Q', 3)
        >>> float(period)
        2000.5
        """
    def __lt__(self, other: Self) -> bool: ...
    def __gt__(self, other: Self) -> bool: ...
    def __le__(self, other: Self) -> bool: ...
    def __ge__(self, other: Self) -> bool: ...
