These subdirectories are populated by running the QCElemental test suite, ``pytest``.
Files are JSON representations of QCSchema instances stored or created in the course of testing.
These in turn are checked for compliance against the exported QCSchema models in test case ``test_qcschema``
by running ``pytest --validate qcelemental/``.
