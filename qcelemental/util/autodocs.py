import re
from enum import Enum, EnumMeta
from textwrap import dedent, indent
from typing import Any

from pydantic import BaseModel, BaseSettings

__all__ = ["auto_gen_docs_on_demand", "get_base_docs", "AutoPydanticDocGenerator"]


class AutoDocError(ValueError):
    """
    Helper error Raised when the autodoc application failed.

    Traps this very specific error and not other ValueErrors
    """


def type_to_string(input_type):
    if type(input_type) is type:
        return input_type.__name__
    else:
        return repr(input_type).replace("typing.", "")


def is_pydantic(test_object):
    try:
        instance = isinstance(test_object, BaseSettings) or isinstance(test_object, BaseModel)
    except TypeError:
        instance = False
    try:
        subclass = issubclass(test_object, BaseSettings) or issubclass(test_object, BaseModel)
    except TypeError:
        subclass = False
    return instance or subclass


def parse_type_str(prop) -> str:
    from pydantic import fields  # Import here to minimize issues

    typing_map = {
        fields.SHAPE_TUPLE: "Tuple",
        fields.SHAPE_SET: "Set",
        fields.SHAPE_LIST: "List",
        fields.SHAPE_SINGLETON: "Union",
    }  # yapf: disable
    if type(prop) is type or prop.__module__ == "typing":
        # True native Python type
        prop_type_str = type_to_string(prop)
    elif issubclass(prop.type_.__class__, Enum) or issubclass(prop.type_.__class__, EnumMeta):
        # Enumerate, have to do the __class__ or issubclass(prop.type_) throws issues later.
        prop_type_str = "{" + ",".join([str(x.value) for x in prop.type_]) + "}"
    elif type(prop.type_) is type and prop.shape == fields.SHAPE_SINGLETON:
        # Native Python type buried in a Field
        prop_type_str = type_to_string(prop.type_)
    elif is_pydantic(prop.type_):
        # Pydantic types
        prop_type_str = f":class:`{prop.type_.__name__}`"
    elif prop.type_.__module__ == "typing":
        # Typing Types
        prop_type_str = ""
        key_field = prop.key_field
        sub_fields = prop.sub_fields
        # Special case of Optional[]
        # if sub_fields is not None and any([sf.sub_fields is type(None) for sf in sub_fields]):
        if sub_fields is not None and any([sf.type_ is type(None) for sf in sub_fields]):
            reconstructed_props = [f for f in sub_fields if f.type_ is not type(None)]
            parsed_types = [parse_type_str(f) for f in reconstructed_props]
            if len(parsed_types) == 1:
                prop_type_str = parsed_types[0]
            else:
                prop_type_str = "Union[" + ", ".join(parsed_types) + "]"
        elif prop.shape == fields.SHAPE_MAPPING:
            prop_type_str = "Dict[" + parse_type_str(key_field) + ", " + parse_type_str(prop.type_) + "]"
        elif sub_fields is not None:
            # Not "optional", but iterable
            prop_type_str = typing_map[prop.shape] + "[" + ", ".join([parse_type_str(sf) for sf in sub_fields]) + "]"
        elif prop.type_ is Any:
            prop_type_str = "Any"
    elif "ConstrainedInt" in prop.type_.__name__:
        prop_type_str = "ConstrainedInt"
    elif "ConstrainedFloat" in prop.type_.__name__:
        prop_type_str = "ConstrainedFloat"
    elif prop.shape in typing_map.keys():
        if prop.sub_fields is None:
            # Single item
            if prop.type_.__module__ == "pydantic.types":
                # A bit of a catch-all
                prop_type_str = prop.type_.__name__
            else:
                prop_type_str = typing_map[prop.shape] + "[" + parse_type_str(prop.type_) + "]"
        else:
            prop_type_str = (
                typing_map[prop.shape] + "[" + ", ".join([parse_type_str(sf) for sf in prop.sub_fields]) + "]"
            )
    else:
        # Finally, with nothing else to do...
        prop_type_str = str(prop)

    return prop_type_str


def doc_formatter(base_docs: str, target_object: BaseModel, allow_failure: bool = True) -> str:
    """
    Generate the docstring for a Pydantic object automatically based on the parameters

    This could use improvement.

    Might be ported to Elemental at some point
    """

    # Convert the None to regex-parsable string
    if base_docs is None:
        doc_edit = ""
    else:
        doc_edit = base_docs

    # Is pydantic and not already formatted
    if is_pydantic(target_object) and not re.search(r"^\s*Parameters\n", doc_edit, re.MULTILINE):
        try:
            # Add the white space
            if not doc_edit.endswith("\n\n"):
                doc_edit += "\n\n"
            # Add Parameters separate
            new_doc = dedent(doc_edit) + "Parameters\n----------\n"
            # Get Pydantic fields
            target_fields = target_object.__fields__
            # Go through each property
            for prop_name, prop in target_fields.items():
                # Handle Type
                prop_type_str = parse_type_str(prop)

                # Handle (optional) description
                prop_desc = prop.field_info.description  # type: ignore

                # Combine in the following format:
                # name : type(, Optional, Default)
                #   description
                first_line = prop_name + " : " + prop_type_str
                if not prop.required and (prop.default is None or is_pydantic(prop.default)):
                    first_line += ", Optional"
                elif prop.default is not None:
                    first_line += f", Default: {prop.default}"
                # Write the prop description
                second_line = "\n" + indent(prop_desc, "    ") if prop_desc is not None else ""
                # Finally, write the detailed doc string
                new_doc += first_line + second_line + "\n"
        except:  # lgtm [py/catch-base-exception]
            if allow_failure:
                new_doc = base_docs
            else:
                raise

    else:
        new_doc = base_docs

    # Assign the new doc string
    return new_doc


class AutoPydanticDocGenerator:
    """
    Dynamic Doc generator, should never be called directly and only though augo_gen_docs_on_demand or as a part of the
    __new__ constructor in a metaclass.
    """

    ALREADY_AUTODOCED_ATTR = "__model_autodoc_applied__"
    AUTODOC_BASE_DOC_REFERENCE_ATTR = "__base_doc__"

    def __init__(self, target: BaseModel, allow_failure: bool = True, always_apply: bool = False):
        # Checks against already instanced and uninstanced classes while avoiding unhahsable type error

        if not always_apply:
            if isinstance(target, BaseModel) or (isinstance(target, type) and issubclass(target, BaseModel)):

                if (
                    hasattr(target, self.ALREADY_AUTODOCED_ATTR)
                    and getattr(target, self.ALREADY_AUTODOCED_ATTR) is True
                ):
                    raise AutoDocError(
                        "Object already has autodoc rules applied to it, cannot re-apply auto documentation"
                        f"without first resetting the __doc__ attribute and setting "
                        f"{self.ALREADY_AUTODOCED_ATTR} to False (or deleting it)"
                    )
            else:
                raise TypeError("Cannot use auto-doc tech on non-BaseModel subclasses")

        self.base_doc = target.__doc__
        setattr(target, self.AUTODOC_BASE_DOC_REFERENCE_ATTR, self.base_doc)
        self.target = target
        setattr(target, self.ALREADY_AUTODOCED_ATTR, True)
        self.allow_failure = allow_failure

    def __get__(self, *args):
        return doc_formatter(self.base_doc, self.target, allow_failure=self.allow_failure)

    def __del__(self):
        try:
            self.target.__doc__ = self.base_doc
            if hasattr(self.target, self.ALREADY_AUTODOCED_ATTR):
                setattr(self.target, self.ALREADY_AUTODOCED_ATTR, False)
        except:  # lgtm [py/catch-base-exception]
            # Corner case where trying to reapply and failing cannot delete the new self mid __init__ since
            # base_doc has not been set.
            pass


def auto_gen_docs_on_demand(
    target: BaseModel, allow_failure: bool = True, ignore_reapply: bool = True, force_reapply: bool = False
):
    """Tell a Pydantic base model to generate its docstrings on the fly with the tech here """
    try:
        target.__doc__ = AutoPydanticDocGenerator(target, allow_failure=allow_failure)  # type: ignore
    except AutoDocError:
        if ignore_reapply:
            pass
        else:
            raise
    # Reapply by force to allow inherited models to auto doc as well
    if force_reapply:
        del target.__doc__
        auto_gen_docs_on_demand(target, allow_failure=allow_failure, ignore_reapply=ignore_reapply, force_reapply=False)


def get_base_docs(target: object):
    """Get the non-auto formatted docs, if present, otherwise just get the basic docstring"""
    if hasattr(target, AutoPydanticDocGenerator.AUTODOC_BASE_DOC_REFERENCE_ATTR):
        return getattr(target, AutoPydanticDocGenerator.AUTODOC_BASE_DOC_REFERENCE_ATTR)
    return target.__doc__
