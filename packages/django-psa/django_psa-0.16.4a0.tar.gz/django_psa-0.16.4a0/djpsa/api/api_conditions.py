class APICondition:
    """A single API condition"""

    _formatter = None

    VALID_OPERATORS = {"and", "or", "==", "!=", ">=", "<=", ">", "<"}

    def __init__(self, *args, op=None, field=None, value=None):
        self._items = []
        self.op = op
        self.field = field
        self.value = value

        if self.op not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: {self.op}. "
                f"Must be one of {self.VALID_OPERATORS}")

        # If grouping (and/or), ensure the args are instances of APICondition
        if self.op in ("and", "or"):
            for condition in args:
                if not isinstance(condition, self.__class__):
                    raise TypeError(
                        f"Grouped conditions must also "
                        f"be instances of {self.__class__.__name__}"
                    )
                self._items.append(condition)

    def __repr__(self):
        if len(self._items):
            return f"GroupedCondition(op={self.op}, conditions={self._items})"
        return \
            f"Condition(op={self.op}, field={self.field}, value={self.value})"

    def format_condition(self):
        """Formats condition using the class-level formatter"""
        if self._formatter:
            return self._formatter.format(self)
        raise NotImplementedError("Formatter not provided for API condition.")

    def is_grouped(self):
        """Checks if the condition is grouped (AND/OR)"""
        return len(self._items) > 0


class APIConditionList:
    """Holds a list of API conditions and formats them"""

    _formatter = None

    def __init__(self):
        self._list = []

    def __getitem__(self, i):
        return self._list[i]

    def __setitem__(self, i, value):
        if not isinstance(value, APICondition):
            raise TypeError("Conditions must be instances of APICondition.")
        self._list[i] = value

    def __repr__(self):
        return f"APIConditionList({self._list})"

    def __len__(self):
        return len(self._list)

    def __delitem__(self, i):
        del self._list[i]

    def __iter__(self):
        return iter(self._list)

    def append(self, condition):
        """Add a new condition to the list"""
        if not isinstance(condition, APICondition):
            raise TypeError("Condition must be an instance of APICondition.")
        self._list.append(condition)

    def build_query(self, method="get", **kwargs):
        """Builds the query by formatting all conditions in the list"""
        queries = []
        for condition in self._list:
            queries.append(condition.format_condition())
        return self._formatter.build_query(queries, method=method, **kwargs)
