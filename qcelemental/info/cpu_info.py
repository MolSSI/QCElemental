"""
Contains metadata about Processors
"""

import difflib
import re
from enum import Enum
from functools import lru_cache
from typing import List, Optional

from pydantic import Field

from ..models import ProtoModel


class VendorEnum(str, Enum):
    """Allowed processor vendors, used for validation.
    """

    amd = "amd"
    intel = "intel"
    nvidia = "nvidia"
    arm = "arm"


class InstructionSetEnum(int, Enum):
    """Allowed instruction sets for CPUs in an ordinal enum.
    """

    none = 0
    sse = 1
    avx = 2
    avx2 = 3
    avx512 = 4


class ProcessorInfo(ProtoModel):
    name: str = Field(..., description="Name of the processor.")
    ncores: int = Field(..., description="The number of physical cores on the chip.")
    nthreads: Optional[int] = Field(..., description="The maximum number of concurrent threads.")
    base_clock: float = Field(..., description="The base clock frequency (GHz).")
    boost_clock: Optional[float] = Field(..., description="The boost clock frequency (GHz).")
    model: str = Field(..., description="The model number of the chip.")
    family: str = Field(..., description="The family of the chip.")
    launch_date: Optional[int] = Field(..., description="The launch year of the chip.")
    target_use: str = Field(..., description="Target use case (Desktop, Server, etc).")
    vendor: VendorEnum = Field(..., description="The vendor the chip is produced by.")
    microarchitecture: Optional[str] = Field(..., description="The microarchitecture the chip follows.")
    instructions: InstructionSetEnum = Field(..., description="The maximum vectorized instruction set available.")
    type: str = Field(..., description="The type of chip (cpu, gpu, etc).")


class ProcessorContext:
    """Information about Process information.

    Parameters
    ----------
    context : {'default'}
        Origin of loaded data.

    Attributes
    ----------
    processors : List[ProcessorInfo]
        A list of all processors known
    index : Dict[(str, str): ProcessorInfo]
        A (vendor, model) index to the processor information
    index_vendor : Dict[str, Dict[str, ProcessorInfo]]
        A vendor, model nested dictionary index for processor information
    name : str
        The name of the context ('default')

    """

    def __init__(self, context: str = "defualt"):
        if context != "default":
            raise KeyError(f"Context set as '{context}'," + " only contexts {'default'} are currently supported")

        from .data import cpu_data_blob

        self.processors: List[ProcessorInfo] = [ProcessorInfo(**data) for data in cpu_data_blob.data_blob]

        self.index = {(x.vendor, self.process_names(x.model)): x for x in self.processors}

        self.index_vendor = {k.name: {} for k in VendorEnum}
        for proc in self.processors:
            self.index_vendor[proc.vendor][self.process_names(proc.model)] = proc

        self.name = context

    def __str__(self) -> str:
        return "ProcessorContext(context='{}')".format(self.name)

    def process_names(self, name):
        name = name.lower()
        name = name.replace("(tm)", "").replace("(r)", "").replace("™", "")
        name = " ".join(name.split())
        name = name.strip()
        return name


context = ProcessorContext("default")


@lru_cache(maxsize=1024)
def get(name: str, vendor=None, cutoff=0.9) -> ProcessorInfo:

    name = context.process_names(name.split("@")[0])

    if ("amd" in name) or (vendor == "amd"):
        vendor = "amd"

        name = re.split(r"\d+-core pro", name)[0]

        # Opteron model names are only numbers?
        if "opteron" in name:
            name = name.replace("processor", "")
            name = name.replace("opteron", "")
            name = name.replace("amd", "")

    elif "intel" in name or (vendor == "intel"):
        vendor = "intel"

        if "xeon" in name:
            name = name.replace(" v", "v")
            if name.endswith(" 0"):
                name = name[:-2]

        name = name.replace("intel", "").replace("cpu", "")
        name = name.replace("core", "").replace("xeon", "")
        name = name.replace("silver", "").replace("gold", "").replace("phi", "")

    if vendor is None:
        raise KeyError("Could not determine vendor, please provide one.")

    index = context.index_vendor[vendor]

    name = context.process_names(name)
    matches = difflib.get_close_matches(name, index.keys(), cutoff=cutoff)

    if matches:
        return index[matches[0]]
    else:
        raise KeyError(f"Could not find processor {vendor}: {name}.")


def list_names():
    return sorted([cpu.name for cpu in context.processors])
