import os
import setuptools
import versioneer

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
            #'pyyaml',
            #'py-cpuinfo',
            #'psutil',
        ],
        extras_require={
            'docs': [
                'sphinx',  # autodoc was broken in 1.3.1
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
            ],
        },
        tests_require=[
            'pytest',
            'pytest-cov',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
        ],
        zip_safe=False,
        long_description="""
""")
