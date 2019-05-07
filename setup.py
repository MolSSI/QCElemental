import os
import sys
import setuptools
import versioneer

short_description = "QCElemental is a resource module for quantum chemistry containing physical"
"constants and periodic table data from NIST and molecule handlers."

# from https://github.com/pytest-dev/pytest-runner#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

try:
    with open("README.md", "r") as handle:
        long_description = handle.read()
except FileNotFoundError:
    long_description = short_description

if __name__ == "__main__":
    setuptools.setup(
        name='qcelemental',
        description='Essentials for Quantum Chemistry.',
        author='The QCArchive Development Team',
        author_email='qcarchive@molssi.org',
        url="https://github.com/MolSSI/QCElemental",
        license='BSD-3C',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        packages=setuptools.find_packages(exclude=['*checkup*']),
        include_package_data=True,
        package_data={'': [os.path.join('qcelemental', 'data', '*.json')]},
        setup_requires=[] + pytest_runner,
        python_requires='>=3.6',
        install_requires=['numpy', 'pint', 'pydantic >= 0.20'],
        extras_require={
            'docs': [
                'numpydoc',
                'sphinx',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
            ],
            'tests': [
                'pytest >= 3.9.1',
                'pytest-cov',
            ],
            'align': [
                'networkx',
            ],
        },
        tests_require=[
            'pytest >= 3.9.1',
            'pytest-cov',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
        zip_safe=False,
        long_description=long_description,
        long_description_content_type="text/markdown")
