import os
import setuptools
import versioneer

short_description = "QCElemental is a resource module for quantum chemistry containing physical"
"constants and periodic table data from NIST and molecule handlers."

try:
    with open("README.md", "r") as handle:
        long_description = handle.read()
except:
    long_description = short_description

if __name__ == "__main__":
    setuptools.setup(
        name='qcelemental',
        description='Essentials for Quantum Chemistry.',
        author='Lori A. Burns',
        author_email='lori.burns@gmail.com',
        url="https://github.com/MolSSI/qcelemental",
        license='BSD-3C',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        packages=setuptools.find_packages(exclude=['*checkup*']),
        include_package_data=True,
        package_data={'': [os.path.join('qcelemental', 'data', '*.json')]},
        install_requires=[
            'numpy',
            'pint',
        ],
        extras_require={
            'docs': [
                'numpydoc',
                'sphinx',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
            ],
            'tests': [
                'deepdiff',
                'pytest',
                'pytest-cov',
            ],
        },
        tests_require=[
            'deepdiff',
            'pytest',
            'pytest-cov',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=False,
        long_description=long_description,
        long_description_content_type="text/markdown"
)
