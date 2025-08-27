from yta_validation import PythonValidator
from typing import Union


class ErrorMessage:
    """
    Class to encapsulate the different error
    messages we need.
    """

    @staticmethod
    def parameter_is_not_a_class(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a class.'
    
    @staticmethod
    def parameter_not_provided(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" was not provided.'
    
    @staticmethod
    def parameter_is_not_string(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a string.'
    
    @staticmethod
    def parameter_is_not_boolean(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not boolean.'
    
    @staticmethod
    def parameter_is_not_int(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not an int.'
    
    @staticmethod
    def parameter_is_not_int_between(
        parameter_name: str,
        lower_limit: int,
        upper_limit: int 
    ) -> str:
        return f'The "{parameter_name}" parameter is not an integer between "{str(lower_limit)}" and "{str(upper_limit)}".'

    @staticmethod
    def parameter_is_not_positive_int(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not a positive int.'

    @staticmethod
    def parameter_is_not_float(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not a float.'
    
    @staticmethod
    def parameter_is_not_positive_float(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not a positive float.'

    @staticmethod
    def parameter_is_not_dict(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not a dict.'
    
    @staticmethod
    def parameter_is_not_callable(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not callable.'

    @staticmethod
    def parameter_is_not_bytes(
        parameter_name: str
    ) -> str:
        return f'The "{parameter_name}" parameter is not bytes.'

    @staticmethod
    def parameter_is_not_number(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a number.'
    
    @staticmethod
    def parameter_is_not_number_between(
        parameter_name: str,
        lower_limit: Union[int, float],
        upper_limit: Union[int, float]
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a number between the "{str(float(lower_limit))}" and "{str(float(upper_limit))}" limits.'

    @staticmethod
    def parameter_is_not_positive_number(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a valid and positive number.'
    
    @staticmethod
    def parameter_is_not_numpy_array(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a numpy array.'
    
    @staticmethod
    def parameter_is_not_numpy_dtype(
        parameter_name: str
    ) -> str:
        return f'The parameter "{parameter_name}" provided is not a numpy dtype.'

    @staticmethod
    def parameter_is_not_tuple(
        parameter_name: str,
        n_elements: Union[None, int]
    ) -> str:
        return (
            f'The provided "{parameter_name}" parameter is not a tuple.'
            if n_elements is None else
            f'The provided "{parameter_name}" parameter is not a tuple of {n_elements} elements.'
        )

    @staticmethod
    def parameter_is_file_that_doesnt_exist(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a file that exists.'
    
    @classmethod
    def parameter_is_not_file_of_file_type(
        parameter_name: str,
        file_type: 'FileType'
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a {file_type.value} filename.'
    
    @staticmethod
    def parameter_is_not_valid_url(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a valid url.'

    @staticmethod
    def parameter_is_not_list_of_string(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of strings.'

    @staticmethod
    def parameter_is_not_list_of_numbers(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of numbers.'
    
    @staticmethod
    def parameter_is_not_list_of_positive_numbers(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a ist of positive numbers.'

    @staticmethod
    def parameter_is_not_list_of_int(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of int numbers.'
    
    @staticmethod
    def parameter_is_not_list_of_float(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of float numbers.'

    @staticmethod
    def parameter_is_not_list_of_classes(
        parameter_name: str,
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of classes.'

    @staticmethod
    def parameter_is_not_list_of_these_classes(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of classes of this group: {", ".join(_cls_parameter_to_string_classes_array(cls))}'

    @staticmethod
    def parameter_is_not_list_of_instances(
        parameter_name: str
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of instances.'
    
    @staticmethod
    def parameter_is_not_list_of_these_instances(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of instances of this group: {", ".join(_cls_parameter_to_string_classes_array(cls))}'
    
    @staticmethod
    def parameter_is_not_list_of_subclasses_of(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a list of subclasses of this group: {", ".join(_cls_parameter_to_string_classes_array(cls))}'
    
    @staticmethod
    def parameter_is_not_numeric_tuple_or_list_or_array_of_2_elements_between_values(
        parameter_name: str,
        first_element_lower_limit: float,
        first_element_upper_limit: float,
        second_element_lower_limit: float,
        second_element_upper_limit: float
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a numeric tuple, list or array of 2 elements between the limits [{str(first_element_lower_limit)}, {str(first_element_upper_limit)}], [{str(second_element_lower_limit)}, {str(second_element_upper_limit)}].'

    @staticmethod
    def parameter_is_not_class_of(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not one of these classes: {", ".join(_cls_parameter_to_string_classes_array(cls))}.'

    @staticmethod
    def parameter_is_not_subclass_of(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        return f'The provided "{parameter_name}" parameter is not a subclass of one of these classes: {", ".join(_cls_parameter_to_string_classes_array(cls))}.'
    
    @staticmethod
    def parameter_is_not_an_instance(
        parameter_name: str
    ) -> str:
        """
        Message that indicates that the 'parameter_name'
        is not an instance.
        """
        return f'The provided "{parameter_name}" parameter is not an instance.'

    @staticmethod
    def parameter_is_not_instance_of(
        parameter_name: str,
        cls: Union[list[Union[type, str]], str, type]
    ) -> str:
        """
        Message that indicates that the 'parameter_name'
        is not any of the provided 'classes'.
        """
        return f'The provided "{parameter_name}" parameter is not an instance of any of these classes: {", ".join(_cls_parameter_to_string_classes_array(cls))}.'

    @staticmethod
    def keys_are_missing_in_dict(
        name: str,
        missing_keys: list[str]
    ) -> str:
        """
        Message that indicates that the dict parameter
        with the given 'name' doesn't have the also given
        'missing_keys' keys set.
        """
        return f'These keys are missing in the "{name}" dict: {", ".join(missing_keys)}'

    @staticmethod
    def parameter_is_not_name_of_ytaenum_class(
        name: str,
        enum
    ) -> str:
        return f'The provided YTAEnum name "{name}" is not a valid {enum.__class__.__name__} YTAEnum name.'
    
    @staticmethod
    def parameter_is_not_value_of_ytaenum_class(
        value: any,
        enum
    ) -> str:
        return f'The provided YTAEnum value "{value}" is not a valid {enum.__class__.__name__} YTAEnum value.'
    
    @staticmethod
    def parameter_is_not_name_nor_value_of_ytaenum_class(
        name_or_value: any,
        enum
    ) -> str:
        return f'The provided YTAEnum name or value "{name_or_value}" is not a valid {enum.__class__.__name__} YTAEnum name or value.'
    
    @staticmethod
    def parameter_is_not_name_nor_value_nor_enum_of_ytaenum_class(
        name_or_value_or_enum: any,
        enum
    ) -> str:
        return f'The provided YTAEnum name, value or instance "{name_or_value_or_enum}" is not a valid {enum.__class__.__name__} YTAEnum name, value or instance.'
    
def _cls_parameter_to_string_classes_array(
    cls: Union[list[Union[type, str]], str, type]
) -> list[str]:
    """
    Transform the given 'cls' class or class array
    to an array of string class name(s).
    """
    # To list
    cls = (
        [cls]
        if not PythonValidator.is_list(cls) else
        cls
    )

    # To str array
    return [
        (
            cls_item
            if PythonValidator.is_string(cls_item) else
            cls_item.__name__ # the name of the class
        ) for cls_item in cls
    ]