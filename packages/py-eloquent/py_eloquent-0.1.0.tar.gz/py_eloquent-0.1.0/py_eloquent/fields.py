from typing import Any

class Field:
    def __init__(self, column_type: str = "TEXT", primary_key: bool = False, default: Any = None, column: str = None):
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.name = column  # set by Model metaclass

class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__(column_type="INT", **kwargs)

class String(Field):
    def __init__(self, length=255, **kwargs):
        super().__init__(column_type=f"VARCHAR({length})", **kwargs)

class Float(Field):
    def __init__(self, **kwargs):
        super().__init__(column_type="FLOAT", **kwargs)

class Boolean(Field):
    def __init__(self, **kwargs):
        super().__init__(column_type="TINYINT(1)", **kwargs)

class DateTime(Field):
    def __init__(self, **kwargs):
        super().__init__(column_type="DATETIME", **kwargs)
