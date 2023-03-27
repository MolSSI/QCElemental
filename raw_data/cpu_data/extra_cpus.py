"""
CPUs not in the JSON sources, but present in QCArchive data
"""

extra_cpus = []

# AMD Opteron(tm) Processor 6168
extra_cpus.append(
    {
        "base_clock": 1_900_000_000,
        "boost_clock": None,
        "family": "AMD Opteron\u2122",
        "instructions": 1,
        "launch_date": 2010,
        "microarchitecture": None,
        "model": "6168",
        "ncores": 12,
        "nthreads": 12,
        "target_use": "Server",
        "type": "cpu",
        "vendor": "amd",
    }
)

# AMD Opteron(tm) Processor 6174
extra_cpus.append(
    {
        "base_clock": 2_200_000_000,
        "boost_clock": None,
        "family": "AMD Opteron\u2122",
        "instructions": 1,
        "launch_date": 2010,
        "microarchitecture": None,
        "model": "6174",
        "ncores": 12,
        "nthreads": 12,
        "target_use": "Server",
        "type": "cpu",
        "vendor": "amd",
    }
)

# Intel(R) Xeon(R) CPU E5-2673 v3 @ 2.40GHz
extra_cpus.append(
    {
        "base_clock": 2_400_000_000,
        "boost_clock": 3_200_000_000,
        "family": "Intel Xeon Processor E5 v3 Family",
        "instructions": 3,
        "launch_date": 2013,
        "microarchitecture": "Ivy Bridge EP",
        "model": "E5-2673V3",
        "ncores": 12,
        "nthreads": 24,
        "target_use": "Server",
        "type": "cpu",
        "vendor": "intel",
    }
)

fixes = {
    ("amd", "AMD EPYC\u2122 7551P"): {"launch_date": 2017},
    ("amd", 6376): {"launch_date": 2012},
    ("amd", 6276): {"launch_date": 2011},
    ("amd", "AMD EPYC\u2122 7401P"): {"launch_date": 2017},
    ("amd", "AMD EPYC\u2122 7601"): {"launch_date": 2017},
    ("amd", 6274): {"launch_date": 2011},
}
