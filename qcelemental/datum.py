"""
Contains the Datum class
"""

import collections

import numpy as np


class Datum(collections.namedtuple('Datum', 'label units data comment DOI glossary')):
    """Facilitates the storage of quantum chemical results by labeling them with basic metadata."""

    def __new__(cls, label, units, data, comment='', doi=None, glossary=''):
        return super(Datum, cls).__new__(cls, label, units, data, comment, doi, glossary)

    def __str__(self, label=''):
        width = 40
        text = ['-' * width, '{:^{width}}'.format('Datum' + self.label, width=width)]
        if label:
            text.append('{:^{width}}'.format(label))
        text.append('-' * width)
        text.append('Data:     {}'.format(self.data))
        text.append('Units:    [{}]'.format(self.units))
        text.append('DOI:      {}'.format(self.DOI))
        text.append('Comment:  {}'.format(self.comment))
        text.append('Glossary: {}'.format(self.glossary))
        text.append('-' * width)
        return '\n'.join(text)

    def to_dict(self):
        dicary = dict(self._asdict())  # dict, not OrderedDict
        for d in ['DOI', 'comment', 'glossary']:
            dicary.pop(d)
        if isinstance(self.data, (np.ndarray, np.number)):
            if self.data.dtype == np.complex:
                dicary['data'] = [dicary['data'].real.tolist(), dicary['data'].imag.tolist()]
            else:
                dicary['data'] = dicary['data'].tolist()
        elif isinstance(self.data, (complex, np.complex)):
            dicary['data'] = [self.data.real, self.data.imag]

        return dicary


def print_variables(qcvars):
    """Form a printable representation of qcvariables.

    Parameters
    ----------
    qcvars : dict of Datum
        Group of Datum objects to print.

    Returns
    -------
    str
        Printable string representation of label, data, and unit in Datum-s.

    """
    text = ['\n  Variable Map:', '  ----------------------------------------------------------------------------']

    if len(qcvars) == 0:
        text.append('  (none)')
        return '\n'.join(text)

    largest_key = max(len(k) for k in qcvars) + 2  # for quotation marks
    largest_characteristic = 8
    for k, v in qcvars.items():
        try:
            exp = int(str(v.data).split('E')[1])
        except IndexError:
            pass
        else:
            largest_characteristic = max(exp, largest_characteristic)

    for k, qca in sorted(qcvars.items()):
        #if k != qca.lbl:
        #    raise ValidationError('Huh? {} != {}'.format(k, qca.label))

        if isinstance(qca.data, np.ndarray):
            data = np.array_str(qca.data, max_line_width=120, precision=8, suppress_small=True)
            data = '\n'.join('        ' + ln for ln in data.splitlines())
            text.append("""  {:{keywidth}} => {:{width}} [{}]""".format(
                '"' + k + '"', '', qca.units, keywidth=largest_key, width=20))
            text.append(data)
        else:
            text.append("""  {:{keywidth}} => {:{width}.{prec}f} [{}]""".format(
                '"' + k + '"', qca.data, qca.units, keywidth=largest_key, width=largest_characteristic + 14, prec=12))

    text.append('')
    return '\n'.join(text)
