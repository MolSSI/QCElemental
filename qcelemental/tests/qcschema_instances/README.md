# QCElemental QCSchema examples

These directories contain JSON representations of QCSchema instances created
by the QCElemental test suite. The model family is encoded in the path:

```
v1/<Model>/qcelemental-<test>.json
v2/<Model>/qcelemental-<test>.json
```

Generate and then validate the corpus with two separate commands:

```
pytest --qcschema-examples
pytest --validate-qcschema-examples
```

Generation removes stale JSON first. Ordinary test runs do not write example
files. ``manifest.json`` records the source revision and counts for the most
recent generated corpus.
