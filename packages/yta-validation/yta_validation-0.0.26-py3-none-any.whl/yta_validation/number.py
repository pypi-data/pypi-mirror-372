from yta_validation import PythonValidator
from typing import Union


class NumberValidator:
    """
    Class to simplify and encapsulate the functionality
    related to validate numeric values.
    """

    @staticmethod
    def is_number(
        element: Union[int, float, str, 'np.number', 'Fraction'],
        do_accept_string_number: bool = False
    ) -> bool:
        """
        Check if the provided 'element' is a numeric value. If
        'do_accept_string_number' is True, it will try to parse
        the 'element' as a float if a string is provided.
        """
        if not PythonValidator.is_instance_of(element, [int, float, str, 'np.number', 'Fraction']):
            return False
        
        if PythonValidator.is_instance_of(element, str):
            if do_accept_string_number:
                try:
                    float(element)
                except:
                    return False
            else:
                return False
            
        return True
    
    @staticmethod
    def is_positive_number(
        element: Union[int, float, str, 'np.number', 'Fraction'],
        do_include_zero: bool = True
    ) -> bool:
        """
        This method checks if the provided 'element' is a numeric type,
        or tries to cast it as a float number if string provided, and
        returns True in the only case that the 'element' is actual a
        number by itself or as a string and it is 0 or above it. If 
        'do_include_zero' is set to False it won't be included.
        """        
        if not NumberValidator.is_number(element, False):
            return False
        
        element = float(element)

        return (
            element >= 0
            if do_include_zero else
            element > 0
        )
    
    @staticmethod
    def is_number_between(
        element: Union[int, float, str, 'np.number', 'Fraction'],
        lower_limit: Union[int, float, str, 'np.number', 'Fraction'],
        upper_limit: Union[int, float, str, 'np.number', 'Fraction'],
        do_include_lower_limit: bool = True,
        do_include_upper_limit: bool = True
    ) -> bool:
        """
        This methods returns True if the provided 'variable' is a valid number
        that is between the also provided 'lower_limit' and 'upper_limit'. It
        will return False in any other case.
        """
        if not NumberValidator.is_number(element, True):
            return False
        
        if (
            not NumberValidator.is_number(lower_limit) or
            not NumberValidator.is_number(upper_limit)
        ):
            return False
        
        element = float(element)
        lower_limit = float(lower_limit)
        upper_limit = float(upper_limit)
        
        # TODO: Should we switch limits if unordered (?)
        # if upper_limit < lower_limit:
        #     raise Exception(f'The provided "upper_limit" parameter {str(upper_limit)} is lower than the "lower_limit" parameter {str(lower_limit)} provided.')

        return (
            lower_limit <= element <= upper_limit
            if (
                do_include_lower_limit and
                do_include_upper_limit
            ) else
            lower_limit <= element < upper_limit
            if do_include_lower_limit else
            lower_limit < element <= upper_limit
            if do_include_upper_limit else
            lower_limit < element < upper_limit
        )
        
    @staticmethod
    def is_int(
        element: int
    ) -> bool:
        """
        Return True if the provided 'element' is an int
        number.
        """
        return PythonValidator.is_instance_of(element, int)
    
    @staticmethod
    def is_float(
        element: float
    ) -> bool:
        """
        Return True if the provided 'element' is a float
        number.
        """
        return PythonValidator.is_instance_of(element, float)

    @staticmethod
    def is_fraction(
        element: 'Fraction'
    ) -> bool:
        """
        Return True if the provided 'element' is a 
        Fraction instance (from fractions or from
        quicktions library).
        """
        return PythonValidator.is_instance_of(element, 'Fraction')

    @staticmethod
    def is_even(
        element: float
    ) -> bool:
        """
        Return True if the provided 'element' is an even
        number, which is a number that results 0 when
        divided by 2. This method considers that the
        provided 'element' is a valid number.
        """
        return element % 2 == 0
    
    @staticmethod
    def is_odd(
        element: float
    ) -> bool:
        """
        Return True if the provided 'element' is an odd
        number, which is a number that results 1 when
        divided by 2. This method considers that the
        provided 'element' is a valid number.
        """
        return element % 2 != 0
    
