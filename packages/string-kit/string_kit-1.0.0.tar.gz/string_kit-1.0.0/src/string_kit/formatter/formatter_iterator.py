from collections.abc import Iterator
from functools import reduce
from typing import Hashable


class FormatterIterator(Iterator):
    def __init__(self,
                 format_string: str,
                 field_prefix: str = "{",
                 field_prefix_escape: str = "{",
                 field_suffix: str = "}",
                 field_suffix_escape: str = "}",
                 conversion_prefix: str = "!",
                 conversion_args_prefix: str = "(",
                 conversion_args_prefix_escape: str = "\\",
                 conversion_args_suffix: str = ")",
                 conversion_args_suffix_escape: str = "\\",
                 conversion_args_separator: str = ",",
                 conversion_args_separator_escape: str = "\\",
                 specification_prefix: str = ":"):
        self._format_string = self._clean_parm(
            format_string,
            "format_string",
            empty_allowed=True
        )

        self._field_prefix = self._clean_parm(
            field_prefix,
            "field_prefix"
        )
        self._field_prefix_escape = self._clean_parm(
            field_prefix_escape,
            "field_prefix_escape"
        )
        self._field_prefix_escaped = \
            self._field_prefix_escape + self._field_prefix

        self._field_suffix = self._clean_parm(
            field_suffix,
            "field_suffix"
        )
        self._field_suffix_escape = self._clean_parm(
            field_suffix_escape,
            "field_suffix_escape",
        )
        self._field_suffix_escaped = \
            self._field_suffix_escape + self._field_suffix

        self._conv_prefix = self._clean_parm(
            conversion_prefix,
            "conversion_prefix"
        )

        self._conv_args_prefix = self._clean_parm(
            conversion_args_prefix,
            "conversion_args_prefix"
        )
        self._conv_args_prefix_escape = self._clean_parm(
            conversion_args_prefix_escape,
            "conversion_args_prefix_escape"
        )
        self._conv_args_prefix_escaped = \
            self._conv_args_prefix_escape + self._conv_args_prefix

        self._conv_args_suffix = self._clean_parm(
            conversion_args_suffix,
            "conversion_args_suffix"
        )
        self._conv_args_suffix_escape = self._clean_parm(
            conversion_args_suffix_escape,
            "conversion_args_suffix_escape"
        )
        self._conv_args_suffix_escaped = \
            self._conv_args_suffix_escape + self._conv_args_suffix

        self._conv_args_separator = self._clean_parm(
            conversion_args_separator,
            "conversion_args_separator"
        )
        self._conv_args_separator_escape = self._clean_parm(
            conversion_args_separator_escape,
            "conversion_args_separator_escape"
        )
        self._conv_args_separator_escaped = \
            self._conv_args_separator_escape + self._conv_args_separator

        self._spec_prefix = self._clean_parm(
            specification_prefix,
            "spec_prefix"
        )

        # parms containing same values are not allowed
        test_parms = {
            "field_prefix": self._field_prefix,
            "field_suffix": self._field_suffix,
            "conversion_prefix": self._conv_prefix,
            "conversion_args_prefix": self._conv_args_prefix,
            "conversion_args_suffix": self._conv_args_suffix,
            "conversion_args_separator": self._conv_args_separator,
            "specification_prefix": self._spec_prefix
        }
        for test_parm, test_parm_value in test_parms.items():
            for test_with_parm, test_with_parm_value in test_parms.items():
                if test_with_parm == test_parm:
                    continue
                elif test_parm_value in test_with_parm_value:
                    raise ValueError(
                        f"Parm value {test_parm_value} for parm {test_parm}"
                        f" must not be equal or contained in parm value"
                        f" {test_with_parm_value} for parm {test_with_parm}"
                    )

    def __next__(self):
        if self._format_string:
            field_name, conv_spec = None, []

            field_tokens = ["field_prefix_escaped",
                            "field_suffix_escaped",
                            "field_prefix",
                            "field_suffix"]
            next_a, pos_a = self._next_nearest(field_tokens)

            if next_a == "field_prefix_escaped":
                literal = self._format_string[:pos_a] + self._field_prefix
                head = pos_a + len(self._field_prefix_escaped)
                self._format_string = self._format_string[head:]
            elif next_a == "field_suffix_escaped":
                literal = self._format_string[:pos_a] + self._field_suffix
                head = pos_a + len(self._field_suffix_escaped)
                self._format_string = self._format_string[head:]
            elif next_a == "field_prefix":
                literal = self._format_string[:pos_a]
                head = pos_a + len(self._field_prefix)
                self._format_string = self._format_string[head:]

                conv_name, conv_args, conv_arg_partial = "", [], ""
                next_item = "field_name"
                while True:
                    curr_item, next_item = next_item, None

                    in_field_tokens = ["field_suffix"]
                    if curr_item in ["field_name", "conv", "spec",
                                     "unknown_in_field"]:
                        in_field_tokens.extend(["conv_prefix",
                                                "spec_prefix"])
                    if curr_item in ["conv", "conv_args"]:
                        in_field_tokens.extend(["conv_args_prefix",
                                                "conv_args_suffix"])
                    if curr_item == "conv_args":
                        in_field_tokens.extend(["conv_args_prefix_escaped",
                                                "conv_args_suffix_escaped",
                                                "conv_args_separator_escaped",
                                                "conv_args_separator"])
                    next_b, pos_b = self._next_nearest(in_field_tokens)

                    if next_b == "conv_prefix":
                        curr_item_value = self._format_string[:pos_b]
                        head = pos_b + len(self._conv_prefix)
                        next_item = "conv"
                    elif next_b == "conv_args_prefix":
                        curr_item_value = self._format_string[:pos_b]
                        if not curr_item == "conv":
                            raise ValueError(
                                f"Field '{field_name}': Unexpected"
                                f" `conversion_arg_prefix`"
                                f" '{self._conv_args_prefix}' in conversion"
                                f" '{conv_name}', did you mean to escape it"
                                f" '{self._conv_args_prefix_escaped}'?"
                            )
                        conv_arg_partial, conv_args = "", []
                        head = pos_b + len(self._conv_args_prefix)
                        next_item = "conv_args"
                    elif next_b == "conv_args_prefix_escaped":
                        curr_item_value = self._format_string[:pos_b] \
                                          + self._conv_args_prefix
                        conv_arg_partial += curr_item_value
                        head = pos_b + len(self._conv_args_prefix_escaped)
                        next_item = curr_item
                    elif next_b == "conv_args_suffix_escaped":
                        curr_item_value = self._format_string[:pos_b] \
                                          + self._conv_args_suffix
                        conv_arg_partial += curr_item_value
                        head = pos_b + len(self._conv_args_suffix_escaped)
                        next_item = curr_item
                    elif next_b == "conv_args_separator_escaped":
                        curr_item_value = self._format_string[:pos_b] \
                                          + self._conv_args_separator
                        conv_arg_partial += curr_item_value
                        head = pos_b + len(self._conv_args_separator_escaped)
                        next_item = curr_item
                    elif next_b == "conv_args_separator":
                        curr_item_value = self._format_string[:pos_b]
                        conv_args.append(conv_arg_partial + curr_item_value)
                        conv_arg_partial = ""
                        head = pos_b + len(self._conv_args_separator)
                        next_item = curr_item
                    elif next_b == "conv_args_suffix":
                        if curr_item == "conv":
                            raise ValueError(
                                f"Field '{field_name}': Unexpected"
                                f" `conversion_arg_suffix`"
                                f" '{self._conv_args_suffix}' before start of"
                                f" conversion parameters, did you mean to"
                                f" escape it '{self._conv_args_suffix_escaped}'"
                                f"?"
                            )
                        curr_item_value = self._format_string[:pos_b]
                        conv_args.append(conv_arg_partial + curr_item_value)
                        conv_spec.append(("conv", (conv_name, conv_args)))
                        head = pos_b + len(self._conv_args_suffix)
                        next_item = "unknown_in_field"
                    elif next_b == "spec_prefix":
                        curr_item_value = self._format_string[:pos_b]
                        head = pos_b + len(self._spec_prefix)
                        next_item = "spec"
                    elif next_b == "field_suffix":
                        curr_item_value = self._format_string[:pos_b]
                        head = pos_b + len(self._field_suffix)
                        next_item = None
                    else:
                        raise ValueError(
                            f"Field '{field_name}': Expected"
                            f" '{self._field_suffix}' before end of string"
                        )

                    if curr_item == "field_name":
                        if not curr_item_value:
                            raise ValueError(f"Missing field name.")
                        field_name = curr_item_value
                    elif curr_item == "conv":
                        if not curr_item_value:
                            raise ValueError(
                                f"Field '{field_name}': Missing conversion"
                                f" name."
                            )
                        conv_name = curr_item_value
                        if not next_item == "conv_args":
                            conv_spec.append(("conv", (conv_name, [])))
                    elif curr_item == "spec":
                        if not curr_item_value:
                            raise ValueError(
                                f"Field '{field_name}': Missing specification"
                                f" name."
                            )
                        conv_spec.append(("spec", curr_item_value))
                    elif curr_item == "unknown_in_field":
                        if curr_item_value:
                            raise ValueError(
                                f"Field '{field_name}': Unknown token"
                                f" '{curr_item_value}'."
                            )

                    self._format_string = self._format_string[head:]

                    if next_item is None:
                        break

            elif next_a == "field_suffix":
                raise ValueError(
                    f"Field closing '{self._field_suffix}' encountered without"
                    f" opening '{self._field_prefix}'"
                )
            else:
                literal = self._format_string
                self._format_string = ""

            if literal or field_name is not None or conv_spec:
                return literal, field_name, conv_spec
            else:
                raise StopIteration
        else:
            raise StopIteration

    def _clean_parm(self,
                    parm: str,
                    parm_name: str,
                    *,
                    empty_allowed: bool = False):
        exception_prefix = f"{self.__class__.__name__}.{parm_name}: "
        if isinstance(parm, str):
            if not parm and not empty_allowed:
                raise ValueError(f"{exception_prefix}cannot be empty")
        else:
            raise TypeError(f"{exception_prefix}expected `str`, got"
                            f" `{parm.__class__.__name__}`")
        return parm

    def _next_nearest(self, tokens: list) -> tuple[None | Hashable, int]:
        positions = {
            None: -1,
            **{token: self._format_string.find(getattr(self, f"_{token}"))
               for token in tokens}
        }

        next_nearest = reduce(lambda last, curr:
                              curr if positions[curr] >= 0
                              and (last is None
                                   or positions[curr] < positions[last])
                              else last,
                              positions)

        return next_nearest, positions[next_nearest]
