SYMBOL = "*"


class InvalidArgumentError(ValueError): 
    pass


class MissingLabelError(KeyError):
    def __init__(self, label: str):
        self.label = label

    def __str__(self):
        return f"Label '{self.label}' is missing."
    
class InvalidClassVarError(Exception):
    def __init__(self):
        super().__init__(
            "Class variables cannot be registered globally. "
            "Register them inside the target class "
            "(e.g., in methods with self.x or s.x)."
        )


class _UnsetExitError(Exception):
    def __init__(self):
        super().__init__(
            "Please set exit_point() before calling this function."
        )

class _FrameAccessError(Exception):
    def __init__(self):
        super().__init__(
            "Could not get the current execution frame."
        )


class _ExitEarly(Exception): 
    pass

   