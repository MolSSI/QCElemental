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
        install_requires=["numpy >= 1.12.0", "pint >= 0.10.0", "pydantic >=1.8.2"],
        extras_require={
            'docs': [
                'numpydoc',
                'sphinx',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                "autodoc-pydantic",
            ],
            'tests': [
                'pytest >= 4.0.0',
                'pytest-cov',
                # 'jsonschema',  # needed for speciality `pytest --validate`
            ],
            'align': [
                'networkx>=2.4.0',
            ],
            'viz': [
                'nglview',
            ],
            'lint': [
                'autoflake',
                'black',
                'isort',
            ],
        },
        tests_require=[
            'pytest >= 4.0.0',
            'pytest-cov',
            # 'jsonschema',  # needed for speciality `pytest --validate`
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ],
        zip_safe=False,
        long_description=long_description,
        long_description_content_type="text/markdown")
