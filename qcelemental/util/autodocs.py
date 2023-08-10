import re
from enum import Enum, EnumMeta
from textwrap import dedent, indent
from typing import Union

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings
from typing_extensions import get_args

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


def parse_type_str(prop: Union[FieldInfo, type]) -> str:
    try:
        # Pydantic
        annotation = prop.annotation
    except (AttributeError, TypeError):
        # Normal Python thing (or at least non-pydantic)
        annotation = prop

    if type(annotation) is type:
        # True native Python type
        prop_type_str = type_to_string(annotation)
    elif issubclass(annotation.__class__, Enum) or issubclass(annotation.__class__, EnumMeta):
        # Enumerate, have to do the __class__ or issubclass(annotation) throws issues later.
        prop_type_str = "{" + ",".join([str(x.value) for x in annotation]) + "}"
    elif is_pydantic(annotation):
        # Pydantic types
        prop_type_str = f":class:`{annotation.__name__}`"
    elif annotation.__module__ == "typing":
        # Typing Types
        prop_type_str = ""
        # In python 3.9 and below, annotations didn't have __name__... so... do it the hard way
        try:
            base_name = annotation.__name__
        except AttributeError:
            splits = re.split(r"\.|\[", str(annotation))
            # typing, {actual object name}, args... So get index 1
            base_name = splits[1]
        # Special case Optional
        annotation_args = get_args(annotation)
        prop_type_str += f"{base_name}"
        if len(annotation_args) > 0:
            prop_type_str += "["
            # Stitch together for all of them
            prop_type_objs = []
            for annotation_arg in annotation_args:
                if annotation_arg in [None, type(None)]:
                    if base_name == "Optional":
                        # Skip the Optional adding "NoneType" to its Union
                        continue
                    prop_type_objs.append("None")
                    continue
                prop_type_objs.append(parse_type_str(annotation_arg))
            prop_type_str += ", ".join(prop_type_objs)
            # Close type
            prop_type_str += "]"
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
            target_fields = target_object.model_fields
            # Go through each property
            for prop_name, prop in target_fields.items():
                # Handle Type
                prop_type_str = parse_type_str(prop)

                # Handle (optional) description
                prop_desc = prop.description  # type: ignore

                # Combine in the following format:
                # name : type(, Optional, Default)
                #   description
                first_line = prop_name + " : " + prop_type_str
                if not prop.is_required() and (prop.default is None or is_pydantic(prop.default)):
                    first_line += ", Nullable"
                elif prop.default not in [None, PydanticUndefined]:
                    first_line += f", Default: {prop.default}"
                # Write the prop description
                second_line = "\n" + indent(prop_desc, "    ") if prop_desc is not None else ""
                # Finally, write the detailed doc string
                new_doc += first_line + second_line + "\n"
        except:
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
        except:
            # Corner case where trying to reapply and failing cannot delete the new self mid __init__ since
            # base_doc has not been set.
            pass


def auto_gen_docs_on_demand(
    target: BaseModel, allow_failure: bool = True, ignore_reapply: bool = True, force_reapply: bool = False
):
    """Tell a Pydantic base model to generate its docstrings on the fly with the tech here"""
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
