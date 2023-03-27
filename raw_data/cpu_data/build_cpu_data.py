import json

import black
import pandas as pd

with open("intel_cpu_database.json", "r") as handle:
    intel_raw = json.loads(handle.read())

with open("AMD_data.json", "r") as handle:
    amd_raw = json.loads(handle.read())
    amd_raw = pd.DataFrame(amd_raw["data"])


### Parse AMD


def parse_amd_clock(name):
    name = name.strip().split()

    if len(name) == 0:
        return None

    name = name[-1]

    if "mhz" in name.lower():
        repl = "mhz"
        coef = 1e6

    elif "ghz" in name.lower():
        repl = "ghz"
        coef = 1e9
    else:
        raise KeyError

    return int(coef * float(name.lower().replace(repl, "").strip()))


def parse_amd_launch(d):
    if d is None:
        return None

    if len(d) == 0:
        return None

    try:
        return int(d.split("/")[-1])
    except ValueError:
        if (d[0] == "Q") or (d[1] == "Q"):
            return int(d[2:].strip())
        if "September" in d:
            return int(d.split()[-1])
        print(d)


amd = pd.DataFrame(index=amd_raw.index)
amd["ncores"] = amd_raw["# of CPU Cores"]
amd["nthreads"] = amd_raw["# of Threads"]
amd["model"] = amd_raw["Model"]
amd["family"] = amd_raw["Family"]
amd["base_clock"] = amd_raw["Base Clock"].apply(parse_amd_clock)
amd["boost_clock"] = amd_raw["Max Boost Clock"].apply(parse_amd_clock)
amd["launch_date"] = amd_raw["Launch Date"].apply(parse_amd_launch)
amd["target_use"] = amd_raw["Platform"]
amd["vendor"] = "amd"

amd["microarchitecture"] = None
amd.loc[amd_raw["Supported Technologies"].str.contains("Zen "), "microarchitecture"] = "Zen"
amd.loc[amd_raw["Supported Technologies"].str.contains("Zen\+"), "microarchitecture"] = "Zen+"
amd.loc[amd_raw["Supported Technologies"].str.contains("Zen\+\+"), "microarchitecture"] = "Zen++"

amd["type"] = "cpu"
# amd.loc[amd['model'].str.contains("APU"), "type"] = "apu"

amd["instructions"] = None

# Each of these families have at least this instruction set
amd.loc[amd_raw["Family"].str.contains("Athlon"), "instructions"] = "sse"
amd.loc[amd_raw["Family"].str.contains("Phenom"), "instructions"] = "sse"
amd.loc[amd_raw["Family"].str.contains("FX-Series"), "instructions"] = "sse"
amd.loc[amd_raw["Family"].str.contains("Opteron"), "instructions"] = "sse"
amd.loc[amd_raw["Family"].str.contains("EPYC"), "instructions"] = "avx2"
amd.loc[amd_raw["Family"].str.contains("Ryzen"), "instructions"] = "avx2"

# Climb the ladder
amd.loc[amd_raw["Supported Technologies"].str.contains("SSE"), "instructions"] = "sse"
amd.loc[amd_raw["Supported Technologies"].str.contains("AVX"), "instructions"] = "avx"
amd.loc[amd_raw["Supported Technologies"].str.contains("AVX2"), "instructions"] = "avx2"

amd.loc[amd_raw["Supported Technologies"].str.contains("Zen"), "instructions"] = "avx2"


### Intel Data

intel_rows = []
for row in list(intel_raw.values())[100:]:
    # #     for k, v in row.items():
    # #         print(k)
    # #         print(v)
    # #         print()

    # Not a processor
    if "Performance" not in row:
        continue

    # Some processors are classified as "Mobile", which are almost certainly in laptops not phones
    # Excluding atom procs instead, since they're the ones the break the parser
    # if row["Essentials"]["Vertical Segment"] == "Mobile":
    #    continue
    if "Intel Atom " in row["name"]:
        continue

    try:
        proc = {
            "ncores": int(row["Performance"]["# of Cores"]),
            "nthreads": row["Performance"].get("# of Threads", None),
            "base_clock": row["Performance"]["Processor Base Frequency"],
            "boost_clock": row["Performance"].get("Max Turbo Frequency", None),
            "model": row["Essentials"].get("Processor Number", None),
            "family": row["Essentials"]["Product Collection"],
            "launch_date": row["Essentials"].get("Launch Date"),
            "target_use": row["Essentials"]["Vertical Segment"],
            "vendor": "intel",
            "microarchitecture": row["Essentials"].get("Code Name"),
            "instructions": row.get("Advanced Technologies", {}).get("Instruction Set Extensions"),
        }
        intel_rows.append(proc)
    except:
        print(row)
        raise


def parse_intel_clock(name):
    if name is None:
        return None

    name = name.lower()

    if "mhz" in name:
        repl = "mhz"
        coef = 1e6

    elif "ghz" in name:
        repl = "ghz"
        coef = 1e9
    else:
        raise KeyError

    name = name.replace(repl, "").strip()

    return int(coef * float(name))


def parse_instructions(inst):
    if inst is None:
        return None

    for i in ["AVX-512", "AVX2", "AVX", "SSE"]:
        if i in inst:
            return i

    return None


def parse_date(d):
    if d is None:
        return None

    month, year = d.split("'")

    return int(year) + 2000


intel = pd.DataFrame(intel_rows)
intel["base_clock"] = intel["base_clock"].apply(parse_intel_clock)
intel["boost_clock"] = intel["boost_clock"].apply(parse_intel_clock)
intel["microarchitecture"] = [x.replace("Products formerly ", "") if x else x for x in intel["microarchitecture"]]
intel["instructions"] = intel["instructions"].apply(parse_instructions)
intel["launch_date"] = intel["launch_date"].apply(parse_date)
intel["type"] = "cpu"

df = pd.concat([amd, intel], sort=True)
df.dropna(how="all", inplace=True)

# Munge instructions
df["instructions"] = df["instructions"].str.lower()
df.loc[df["instructions"] == "avx-512", "instructions"] = "avx512"
df.loc[df["instructions"].isnull(), "instructions"] = "none"

translation = {"none": 0, "sse": 1, "avx": 2, "avx2": 3, "avx512": 4}
df["instructions"] = df["instructions"].apply(lambda x: translation[x])


# add extra data
import extra_cpus

for i in extra_cpus.extra_cpus:
    df = df.append(i, ignore_index=True)


def name(vendor, family, model, clock_speed):
    if vendor.lower() in family.lower():
        vendor = ""
    if family in str(model):
        family = ""
    if family.endswith("Processors") and family[: -len("Processors")] in str(model):
        family = ""

    return f"{vendor} {family} {model} @ {clock_speed/1_000_000_000:.1f} GHz"


df["name"] = df.apply(lambda row: name(row["vendor"], row["family"], row["model"], row["base_clock"]), axis=1)

for (vendor, model), fix in extra_cpus.fixes.items():
    idx = df[(df["vendor"] == vendor) & (df["model"] == model)].index
    for k, v in fix.items():
        df.loc[idx, k] = v
# Print some data for posterity
print(df[df["vendor"] == "intel"].tail())
print(df[df["vendor"] == "amd"].tail())
print("---")

# Handle nthreads == ncore bugs
mask = (df["nthreads"] == "") | df["nthreads"].isnull()
df.loc[mask, "nthreads"] = df.loc[mask, "ncores"]

mask = (df["nthreads"] != "") & df["nthreads"].notnull()
# print(df[~mask])
cnt = df.shape[0]
df = df[mask]
print(f"Dropped {cnt - df.shape[0]} / {cnt} processors without ncores")

# Strip out bad models

cnt = df.shape[0]
df = df[~(df["model"].isnull() & (df["launch_date"].isnull() | df["launch_date"] < 2008))]
print(f"Dropped {cnt - df.shape[0]} / {cnt} processors without model numers")


df.sort_values(["vendor", "model", "launch_date"], inplace=True)
df.drop_duplicates(subset=["vendor", "model"], keep="last", inplace=True)


output = f'''
"""
Processor data from multiple sources and vendors.

File Authors: QCElemental Authors
"""

'''


def to_python_str(data):
    return (
        json.dumps(data, indent=2)
        .replace("true", "True")
        .replace("false", "False")
        .replace("NaN", "None")
        .replace("null", "None")
    )


output += f"data_rows = {to_python_str([tuple(x[1].values) for x in df.iterrows()])}\n"
output += f"data_columns = {to_python_str(list(df.columns))}\n"
output += "data_blob = [{k: v for k, v in zip(data_columns, row)} for row in data_rows]\n"

output = black.format_str(output, mode=black.FileMode())

fn = "cpu_data_blob.py"
with open(fn, "w") as handle:
    handle.write(output)
