import pytest

from qcelemental.info import cpu_info, dft_info


@pytest.mark.parametrize(
    "functional,ansatz", [("svwn", 0), ("b3lyp", 1), ("b3lyp-d3", 1), ("b3lyp-nlc", 1), ("dsd-blyp", 1)]
)
def test_dft_info_names(functional, ansatz):
    assert dft_info.get(functional).ansatz == ansatz


def test_cpu_info_index_lengths():
    assert len(cpu_info.context.processors) == len(cpu_info.context.index), "Duplicates found in Index."


@pytest.mark.parametrize(
    "name, model",
    [
        ("AMD Ryzen Threadripper 1950X 16-Core Processor", "AMD Ryzen™ Threadripper™ 1950X"),
        ("AMD Opteron(tm) Processor 6376", "6376"),
        ("AMD EPYC 7601 32-Core Processor", "AMD EPYC™ 7601"),
        ("AMD EPYC 7551P 32-Core Processor", "AMD EPYC™ 7551P"),
        ("Intel(R) Xeon Phi(TM) CPU 7230 @ 1.30GHz", "7230"),
        ("Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz", "6130"),
        ("Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz", "4214"),
        ("Intel(R) Xeon(R) CPU E5-2683 v4 @ 2.10GHz", "E5-2683V4"),
        ("Intel(R) Xeon(R) CPU           X5660  @ 2.80GHz", "X5660"),
        ("Intel(R) Xeon(R) CPU E7-8867 v4 @ 2.40GHz", "E7-8867V4"),
        # Not yet in our database
        # ("Intel(R) Core(TM) i7-7820HQ CPU @ 2.90GHz", "asdf"),
        # ("Intel(R) Core(TM) i5-7360U CPU @ 2.30GHz", "asdf"),
    ],
)
def test_cpu_info_search(name, model):

    cpu = cpu_info.get(name)
    assert cpu is not None, name
    assert cpu.model == model, name


def test_cpu_info_errors():

    with pytest.raises(KeyError) as exc:
        cpu_info.get("E7-8867 V4")

    assert "not determine vendor" in str(exc)

    with pytest.raises(KeyError) as exc:
        cpu_info.get("Intel E0-9999 V4")

    assert "intel: e0-9999" in str(exc)


def test_cpu_info_matches():
    assert cpu_info.get("E7-8867 V4", vendor="intel").model == "E7-8867V4"
