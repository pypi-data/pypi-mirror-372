
from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from yta_validation.error_message import ErrorMessage
from array import array
from typing import Union


class ParameterValidator:
    """
    Class to wrap and simplify the method parameters
    validation, so you are able to validate if a
    parameter is a mandatory string, if it is a 
    positive value, and normalize the exception
    messages.

    The type of the parameters passed to each method
    validation is not validated, so pay attention to
    what you pass there.

    Each method will raise an Exception with a custom
    message if failing.
    """

    @staticmethod
    def validate_mandatory(
        name: str,
        value: any
    ) -> None:
        """
        Validate if the provided 'value' is not None.
        """
        if value is None:
            raise Exception(ErrorMessage.parameter_not_provided(name))

    @staticmethod
    def validate_string(
        name: str,
        value: Union[str, None],
        do_accept_empty: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is of string type.
        """
        if (
            (
                value is not None and
                not PythonValidator.is_string(value)
            ) or
            (
                value == '' and
                not do_accept_empty
            )
        ):
            raise Exception(ErrorMessage.parameter_is_not_string(name))
        
    @staticmethod
    def validate_mandatory_string(
        name: str,
        value: str,
        do_accept_empty: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is a non-empty
        string.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_string(name, value)

        if (
            not do_accept_empty and
            value == ''
        ):
            raise Exception(ErrorMessage.parameter_not_provided(name))
    
    @staticmethod
    def validate_bool(
        name: str,
        value: Union[bool, None]
    ) -> None:
        """
        Validate if the provided 'value' is bool value or not.
        """
        if (
            value is not None and
            not PythonValidator.is_boolean(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_boolean(name))
        
    @staticmethod
    def validate_mandatory_bool(
        name: str,
        value: bool
    ) -> None:
        """
        Validate if the provided 'value' is not None and is
        a boolean value.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_bool(name, value)

    @staticmethod
    def validate_dict(
        name: str,
        value: Union[dict, None]
    ) -> None:
        """
        Validate if the provided 'value' is a dict.
        """
        if (
            value is not None and
            not PythonValidator.is_dict(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_dict(name))

    @staticmethod
    def validate_mandatory_dict(
        name: str,
        value: dict
    ) -> None:
        """
        Validate if the provided 'value' is not None and is
        a dict.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_dict(name, value)

    @staticmethod
    def validate_callable(
        name: str,
        value: Union[callable, None]
    ) -> None:
        """
        Validate if the provided 'value' is callable.
        """
        if (
            value is not None and
            not PythonValidator.is_callable(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_callable(name))
        
    @staticmethod
    def validate_mandatory_callable(
        name: str,
        value: callable
    ) -> None:
        """
        Validate if the provided 'value' is not None and
        is callable.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_callable(name, value)

    @staticmethod
    def validate_bytes(
        name: str,
        value: bytes
    ) -> None:
        """
        Validate if the provided 'value' is bytes.
        """
        if (
            value is not None and
            not PythonValidator.is_bytes(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_bytes(name))
        
    @staticmethod
    def validate_mandatory_bytes(
        name: str,
        value: bytes
    ) -> None:
        """
        Validate if the provided 'value' is not None and
        is bytes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_bytes(name, value)

    @staticmethod
    def validate_int(
        name: str,
        value: int
    ) -> None:
        """
        Validate if the provided 'value' is an int.
        """
        if (
            value is not None and
            not NumberValidator.is_int(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_int(name))

    @staticmethod
    def validate_mandatory_int(
        name: str,
        value: int
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is an int.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_int(name, value)

    @staticmethod
    def validate_int_between(
        name: str,
        value: int,
        lower_limit: int,
        upper_limit: int
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is an int between the given 'lower_limit'
        and 'upper_limit'.
        """
        ParameterValidator.validate_int(name, value)

        if (
            value is not None and
            not NumberValidator.is_number_between(value, lower_limit, upper_limit)
        ):
            raise Exception(ErrorMessage.parameter_is_not_int_between(name, lower_limit, upper_limit))

    def validate_positive_int(
        name: str,
        value: int,
        do_include_zero: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is a positive
        int number.
        """
        if (
            value is not None and
            (
                not NumberValidator.is_int(value) or
                not NumberValidator.is_positive_number(value, do_include_zero = do_include_zero)
            )
        ):
            raise Exception(ErrorMessage.parameter_is_not_positive_int(name))
        
    def validate_mandatory_positive_int(
        name: str,
        value: int,
        do_include_zero: bool = True
    ):
        """
        Validate if the provided 'value' is not None
        and is a positive int number.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_positive_int(name, value, do_include_zero = do_include_zero)

    @staticmethod
    def validate_float(
        name: str,
        value: float
    ) -> None:
        """
        Validate if the provided 'value' is a float.
        """
        if (
            value is not None and
            not NumberValidator.is_float(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_float(name))

    @staticmethod
    def validate_mandatory_float(
        name: str,
        value: float
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a float.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_float(name, value)

    @staticmethod
    def validate_positive_float(
        name: str,
        value: float,
        do_include_zero: bool = True
    ):
        """
        Validate if the provided 'value' is a positive
        int number.
        """
        if (
            value is not None and
            (
                not NumberValidator.is_float(value) or
                not NumberValidator.is_positive_number(value, do_include_zero = do_include_zero)
            )
        ):
            raise Exception(ErrorMessage.parameter_is_not_positive_float(name))
        
    def validate_mandatory_positive_float(
        name: str,
        value: float,
        do_include_zero: bool = True
    ):
        """
        Validate if the provided 'value' is not None
        and is a positive float number.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_positive_float(name, value, do_include_zero = do_include_zero)


    @staticmethod
    def validate_positive_number(
        name: str,
        value: Union[float, int, None],
        do_include_zero: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is a positive number
        or not.
        """
        if (
            value is not None and
            not NumberValidator.is_positive_number(value, do_include_zero = do_include_zero)
        ):
            raise Exception(ErrorMessage.parameter_is_not_positive_number(name))
        
    @staticmethod
    def validate_mandatory_positive_number(
        name: str,
        value: Union[float, int],
        do_include_zero: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is not None and is a
        positive number or not.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_positive_number(name, value, do_include_zero = do_include_zero)

    @staticmethod
    def validate_number(
        name: str,
        value: Union[float, int, None]
    ) -> None:
        """
        Validate if the provided 'value' is a number.
        """
        if (
            value is not None and
            not NumberValidator.is_number(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_number(name))
        
    @staticmethod
    def validate_mandatory_number(
        name: str,
        value: Union[float, int]
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a number.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_number(name, value)

    @staticmethod
    def validate_number_between(
        name: str,
        value: Union[float, int, None],
        lower_limit: Union[float, int],
        upper_limit: Union[float, int]
    ) -> None:
        """
        Validate if the provided 'value' is a number
        between the given 'lower_limit' and 'upper_limit'.
        """
        ParameterValidator.validate_number(name, value)

        if (
            value is not None and
            not NumberValidator.is_number_between(value, lower_limit, upper_limit)
        ):
            raise Exception(ErrorMessage.parameter_is_not_number_between(name, lower_limit, upper_limit))
        
    def validate_mandatory_number_between(
        name: str,
        value: Union[float, int],
        lower_limit: Union[float, int],
        upper_limit: Union[float, int]
    ) -> None:
        """
        Validate if the provided 'value' is not None and
        is a number between the given 'lower_limit' and
        'upper_limit'.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_number_between(name, value, lower_limit, upper_limit)

    @staticmethod
    def validate_numpy_array(
        name: str,
        value: Union['np.ndarray', None]
    ) -> None:
        """
        Validate if the provided 'value' is a numpy
        array.
        """
        if (
            value is not None and
            not PythonValidator.is_numpy_array(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_numpy_array(name))
        
    @staticmethod
    def validate_mandatory_numpy_array(
        name: str,
        value: 'np.ndarray'
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a numpy array.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_numpy_array(name, value)

    @staticmethod
    def validate_numpy_dtype(
        name: str,
        value: Union['np.dtype', None]
    ) -> None:
        """
        Validate if the provided 'value' is a numpy
        dtype.
        """
        if (
            value is not None and
            not PythonValidator.is_numpy_dtype(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_numpy_dtype(name))

    @staticmethod
    def validate_mandatory_numpy_dtype(
        name: str,
        value: 'np.dtype'
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a numpy dtype.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_numpy_dtype(name, value)

    @staticmethod
    def validate_tuple(
        name: str,
        value: Union[tuple, None],
        n_elements: Union[int, None] = None
    ) -> None:
        """
        Validate if the provided 'value' is a tuple of
        'n_elements' (if provided).
        """
        if (
            value is not None and
            (
                not PythonValidator.is_tuple(value) or
                (
                    n_elements is not None and
                    len(value) != n_elements
                )
            )
        ):
            raise Exception(ErrorMessage.parameter_is_not_tuple(name, n_elements))
        
    @staticmethod
    def validate_mandatory_tuple(
        name: str,
        value: tuple,
        n_elements: Union[int, None] = None
    ):
        """
        Validate if the provided 'value' is not None
        and is a tuple of 'n_elements' elements.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_tuple(name, value, n_elements)

    @staticmethod
    def validate_instance(
        name: str,
        value: Union[object, None]
    ) -> None:
        """
        Validate if the provided 'value' is an instance.
        """
        if (
            value is not None and
            not PythonValidator.is_an_instance(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_an_instance(name))
        
    @staticmethod
    def validate_instance_of(
        name: str,
        value: Union[object, None],
        cls: Union[type, str, list[Union[type, str]]]
    ) -> None:
        """
        Validate if the provided 'value' is an instance of the
        given 'cls' class or classes.
        """
        if (
            value is not None and
            not PythonValidator.is_instance_of(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_instance_of(name, cls))

    @staticmethod
    def validate_mandatory_instance_of(
        name: str,
        value: object,
        cls: list[Union[object, str]]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is an
        instance of the given 'cls' classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_instance_of(name, value, cls)

    @staticmethod
    def validate_class_of(
        name: str,
        value: Union[type, None],
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is one of the given
        'cls' classes.
        """
        if (
            value is not None and
            not PythonValidator.is_class(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_class_of(name, cls))
        
    @staticmethod
    def validate_mandatory_class_of(
        name: str,
        value: type,
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is 
        one of the given 'cls' classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_class_of(name, value, cls)

    @staticmethod
    def validate_subclass_of(
        name: str,
        value: type,
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is 
        a subclass of one of the given 'cls' classes.
        """
        if (
            value is not None and
            not PythonValidator.is_subclass_of(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_subclass_of(name, cls))

    @staticmethod
    def validate_mandatory_subclass_of(
        name: str,
        value: type,
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is 
        a subclass of one of the given 'cls' classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_subclass_of(name, value, cls)

    @staticmethod
    def validate_list_of_subclasses_of(
        name: str,
        value: type,
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is a subclass
        of one of the given 'cls' classes.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_subclasses_of(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_subclasses_of(name, cls))

    @staticmethod
    def validate_mandatory_list_of_subclasses_of(
        name: str,
        value: type,
        cls: list[Union[type, str]]
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a subclass of one of the given 'cls'
        classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_subclasses_of(name, value, cls)

    @staticmethod
    def validate_list_of_numbers(
        name: str,
        value: Union[list[Union[int, float]], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of numbers.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_numbers(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_numbers(name))

    @staticmethod
    def validate_mandatory_list_of_numbers(
        name: str,
        value: list[Union[int, float]]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is a
        list of numbers.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_numbers(name, value)

    @staticmethod
    def validate_list_of_positive_numbers(
        name: str,
        value: Union[list[Union[int, float]], None],
        do_include_zero: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is a list of 
        positive numbers.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_positive_numbers(value, do_include_zero = do_include_zero)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_positive_numbers(name))

    @staticmethod
    def validate_mandatory_list_of_positive_numbers(
        name: str,
        value: list[Union[int, float]],
        do_include_zero: bool = True
    ) -> None:
        """
        Validate if the provided 'value' is not None and is a
        list of positive numbers.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_positive_numbers(name, value, do_include_zero = do_include_zero)

    @staticmethod
    def validate_list_of_int(
        name: str,
        value: Union[list[int], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of
        int values.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_int(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_int(name))
        
    @staticmethod
    def validate_mandatory_list_of_int(
        name: str,
        value: list[int]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is a
        list of int numbers.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_int(name, value)

    @staticmethod
    def validate_list_of_float(
        name: str,
        value: Union[list[float], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of
        float values.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_float(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_float(name))
        
    @staticmethod
    def validate_mandatory_list_of_float(
        name: str,
        value: list[float]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is a
        list of float numbers.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_float(name, value)

    @staticmethod
    def validate_list_of_string(
        name: str,
        value: Union[list[str], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of string
        values.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_string(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_string(name))
        
    @staticmethod
    def validate_mandatory_list_of_string(
        name: str,
        value: list[str]
    ) -> None:
        """
        Validate if the provided 'value' is not None and is
        a list of string values.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_string(name, value)

    @staticmethod
    def validate_list_of_instances(
        name: str,
        value: Union[list[object], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of 
        instances.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_instances(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_instances(name))
        
    @staticmethod
    def validate_mandatory_list_of_instances(
        name: str,
        value: list[object]
    ) -> None:
        """
        Validate if the provided 'value' is not None and
        is a list of instances.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_instances(name, value)
        
    @staticmethod
    def validate_list_of_these_instances(
        name: str,
        value: Union[list[object], None],
        cls: Union[list[Union[type, str]], str, type]
    ) -> None:
        """
        Validate if the provided 'value' is a list of 
        instances of the given 'cls' class or classes.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_these_instances(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_these_instances(name, cls))
        
    @staticmethod
    def validate_mandatory_list_of_these_instances(
        name: str,
        value: list[object],
        cls: Union[list[Union[type, str]], str, type]
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a list of instances of the given 'cls'
        class or classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_these_instances(name, value, cls)

    @staticmethod
    def validate_list_of_classes(
        name: str,
        value: Union[list[type], None]
    ) -> None:
        """
        Validate if the provided 'value' is a list of
        classes.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_classes(value)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_classes(name))
        
    @staticmethod
    def validate_mandatory_list_of_classes(
        name: str,
        value: list[type]
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a list of classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_classes(name, value)

    @staticmethod
    def validate_list_of_these_classes(
        name: str,
        value: Union[list[type], None],
        cls: Union[list[Union[type, str]], str, type]
    ) -> None:
        """
        Validate if the provided 'value' is a list
        of the given 'cls' class or classes.
        """
        if (
            value is not None and
            not PythonValidator.is_list_of_these_classes(value, cls)
        ):
            raise Exception(ErrorMessage.parameter_is_not_list_of_these_classes(name, cls))

    @staticmethod
    def validate_mandatory_list_of_these_classes(
        name: str,
        value: list[type],
        cls: Union[list[Union[type, str]], str, type]
    ) -> None:
        """
        Validate if the provided 'value' is not None
        and is a list of the given 'cls' class or
        classes.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_list_of_these_classes(name, value, cls)

    @staticmethod
    def validate_numeric_tuple_or_list_or_array_of_2_elements_between_values(
        name: str,
        value: Union[tuple, list, array],
        first_element_lower_limit: float,
        first_element_upper_limit: float,
        second_element_lower_limit: float,
        second_element_upper_limit: float
    ):
        """
        Validate if the provided 'value' is a numeric
        list, tuple or array of 2 elements that are
        between the given limits.
        """
        if (
            value is not None and
            not PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(value, first_element_lower_limit, first_element_upper_limit, second_element_lower_limit, second_element_upper_limit)
        ):
            raise Exception(ErrorMessage.parameter_is_not_numeric_tuple_or_list_or_array_of_2_elements_between_values(name, first_element_lower_limit, first_element_upper_limit, second_element_lower_limit, second_element_upper_limit))
        
    @staticmethod
    def validate_mandatory_numeric_tuple_or_list_or_array_of_2_elements_between_values(
        name: str,
        value: Union[tuple, list, array],
        first_element_lower_limit: float,
        first_element_upper_limit: float,
        second_element_lower_limit: float,
        second_element_upper_limit: float
    ):
        """
        Validate if the provided 'value' is not None and
        a numeric list, tuple or array of 2 elements that
        are between the given limits.
        """
        ParameterValidator.validate_mandatory(name, value)
        ParameterValidator.validate_numeric_tuple_or_list_or_array_of_2_elements_between_values(name, value, first_element_lower_limit, first_element_upper_limit, second_element_lower_limit, second_element_upper_limit)

    @staticmethod
    def validate_dict_has_keys(
        name: str,
        value: dict,
        keys: list[str]
    ) -> None:
        """
        Validate if the provided 'value' dict has or
        not the also given 'keys', raising an Exception
        if not.
        """
        missing_keys = PythonValidator.get_missing_keys_in_dict(value, keys)

        if missing_keys.length > 0:
            raise Exception(ErrorMessage.keys_are_missing_in_dict(name, missing_keys))