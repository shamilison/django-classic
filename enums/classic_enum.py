__author__ = 'shamil_sakib'

from enum import Enum


class ClassicEnum(Enum):

    @classmethod
    def get_choice_list(cls, include_empty=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_empty: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """
        options = list()
        for e in cls:
            options.append((e.value, e.name))
        options = sorted(options, key=lambda x: x[1])
        if include_empty:
            options = [(None, empty_label)] + options
        return options
