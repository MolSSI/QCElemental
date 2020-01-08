import psi4
import json
import black

dft_info = {'version': psi4.__version__, "functionals": {}}

empirical_dispersion_suffixes = {"-nl", "-d", "-d2", "-d3", "-d3(bj)", "-d3bj", "-d3zero", "-d3m", "-d3mzero", "-d3mbj", "-d3m(bj)"}

for functional in psi4.driver.proc.dft.functionals:
    if any(functional.endswith(suffix) for suffix in empirical_dispersion_suffixes):
        continue

    a = psi4.driver.proc.dft.build_superfunctional(functional, False)[0]
    info = {}
    info["ansatz"] = a.ansatz()
    info["c_hybrid"] = a.is_c_hybrid()
    info["x_hybrid"] = a.is_x_hybrid()
    info["c_lrc"] = a.is_c_lrc()
    info["x_lrc"] = a.is_x_lrc()
    info["nlc"] = a.needs_vv10()
    info["deriv"] = a.deriv()
    dft_info["functionals"][functional] = info


output = f'''
"""
This is a automatically generated file from Psi4's density functional metadata.
Psi4 Version: {psi4.__version__}

File Authors: QCElemental Authors
"""


'''

output += f"psi4_dft_info = {json.dumps(dft_info)}".replace("true", "True").replace("false", "False")

output = black.format_str(output, mode=black.FileMode())

fn = "psi4_dft_info.py"
with open(fn, "w") as handle:
    handle.write(output)