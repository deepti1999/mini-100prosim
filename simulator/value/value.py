import abc
import enum
import locale

from sympy import Symbol, solve, sympify, Equality


class Unit(enum.Enum):
    kWh = 'kWh'
    MWh = 'MWh'
    GWh = 'GWh'
    m = 'm'
    km = 'km'
    percent = '%'
    ha = 'ha'
    MWh_per_ha = 'MWh/ha'
    noUnit = ''


class Value(abc.ABC):
    # Abstract class for Values

    def __init__(self, vid: str, unit: Unit):
        self.__id = vid
        self.__unit = unit
        self.__valFac = None
        self.__free_id = None
        self._orig_value = 0

    @property
    @abc.abstractmethod
    def value(self) -> float:
        raise NotImplementedError("Should have implemented this")

    @value.setter
    @abc.abstractmethod
    def value(self, new_val):
        raise NotImplementedError("Should have implemented this")

    @abc.abstractmethod
    def contains_id(self, vid) -> bool:
        pass

    @property
    def unit(self) -> Unit:
        return self.__unit

    @property
    def id(self) -> str:
        return self.__id

    @property
    def value_factory(self):
        return self.__valFac

    @value_factory.setter
    def value_factory(self, val_fac):
        self.__valFac = val_fac

    @property
    def free_id(self):
        return self.__free_id

    @free_id.setter
    def free_id(self, free_id):
        self.__free_id = free_id

    @property
    def orig_value(self) -> float:
        return self._orig_value

    @property
    def has_changed(self) -> bool:
        return self.value != self.orig_value

    def __str__(self):
        try:
            locale.setlocale(locale.LC_ALL, 'de')
        except locale.Error:
            # If German locale is not available, use default locale
            locale.setlocale(locale.LC_ALL, '')
        mark = ''
        if self.has_changed:
            mark = ' (!)'

        if self.unit == Unit.noUnit:
            return self.id + ' = ' + locale.format('%.2f', self.value, True) + mark
        else:
            return self.id + ' = ' + locale.format('%.2f', self.value, True) \
                                   + " " + str(self.unit.value) + mark


class SimpleValue(Value):

    def __init__(self, vid, val: float, unit: Unit):
        super(SimpleValue, self).__init__(vid, unit)
        self.__value = val
        self._orig_value = val
        self.free_id = vid

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, new_val):
        if self.id == self.free_id:
            self.__value = new_val

    def contains_id(self, vid) -> bool:
        return self.id == vid


class FormulaValue(Value):

    def __init__(self, vid, formula, unit, free_id, value_factory):
        super(FormulaValue, self).__init__(vid, unit)
        self.__formula = formula
        self.free_id = free_id
        self.value_factory = value_factory
        self._orig_value = self.value

    @property
    def value(self) -> float:
        # solve equality with all depending values:
        eq = self.__get_equality()
        for sym in eq.free_symbols:                   # loop over all symbols in equality
            if sym.name != self.id:                   # if not result, substitute by value:
                dep_value = self.value_factory.value(sym.name)
                if dep_value is None:
                    raise ValueError(f"Missing dependency: {sym.name} for formula {self.id}")
                eq = eq.subs(sym, dep_value.value)
        return float(solve(eq, Symbol(self.id))[0])   # uniquely solve equality --> use 1st (and only) result

    @value.setter
    def value(self, new_value):
        if self.contains_id(self.free_id) is False:
            return

        # solve equality for given free variable:
        eq = self.__get_equality()
        for sym in eq.free_symbols:                   # loop over all symbols in equality
            if sym.name not in [self.free_id, self.id]:   # if not result or free variable, substitute by value:
                eq = eq.subs(sym, self.value_factory.value(sym.name).value)
            elif sym.name == self.id:                 # if result, substitute by new value
                eq = eq.subs(sym, new_value)

        val_free_id = solve(eq, Symbol(self.free_id))[0]      # uniquely solve equality --> use 1st (and only) result
        self.value_factory.value(self.free_id).value = val_free_id  # set new value in value collection

    def contains_id(self, vid) -> bool:
        if self.id == vid:
            return True
        else:
            for sym in self.__get_equality().free_symbols:
                if sym.name == vid:
                    return True

        return False

    def __get_equality(self) -> Equality:
        return sympify("Eq(" + self.__formula + "," + self.id + ")")   # parse equality from value id

    def __str__(self):
        return super(FormulaValue, self).__str__() + ' (= ' + self.__formula + ')'
