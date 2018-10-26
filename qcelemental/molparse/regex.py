# remember to use re.VERBOSE with NUCLEUS, NUMBER, VERSION_PATTERN

NUCLEUS = r"""(?:
   (?P<gh1>@)|(?P<gh2>Gh\())?                # optional ghost: @stuff or Gh(stuff) ...
        (                                    # mandatory element: AEuser or Zuser
            (?P<label1>
                (?P<A>\d+)?                  # optional mass number, A
                (?P<E>[A-Z]{1,3})            # mandatory atomic symbol, E
                (?P<user1>(_\w+)|(\d+))?) |  # optional user label: Enumber or E_alphanum
            (?P<label2>
                (?P<Z>\d{1,3})               # mandatory atomic number, Z
                (?P<user2>(_\w+))?)          # optional user label: Z_alphanum
        )
        (?:@(?P<mass>\d+\.\d+))?             # optional mass value [u]
   (?(gh2)\)                                 # ... ghost
          )"""

NUMBER = r"""(
    (?:[-+]?\d*\.\d+(?:[DdEe][-+]?\d+)?) |   # .num with optional sign, exponent, wholenum
    (?:[-+]?\d+\.\d*(?:[DdEe][-+]?\d+)?) |   # num. with optional sign, exponent, decimals
    (?:[-+]?\d+(?:[DdEe][-+]?\d+)?)          # num with optional sign, exponent
         )"""

SEP = r"""[\t ,]+"""
ENDL = r"""[\t ,]*$"""

CHGMULT = r"""(?P<chg>""" + NUMBER + r')' + SEP + r"""(?P<mult>\d+)"""
CARTXYZ = r'(?P<x>' + NUMBER + r')' + SEP + r'(?P<y>' + NUMBER + r')' + SEP + r'(?P<z>' + NUMBER + r')'

# PEP 440 valid versions
# * to avoid dependency on module "packaging", copied from https://github.com/pypa/packaging/blob/master/packaging/version.py#L182-L213
# * Deliberately not anchored to the start and end of the string, to make it easier for 3rd party code to reuse
VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""
