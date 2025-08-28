# `glossing`

Simple utilities and models for handling interlinear glossed text (IGT) in Python. Useful for training models for IGT generation.

```shell
pip install glossing
```

```python
from glossing import IGT

example = IGT(transcription='los gatos corren',
              translation='the cats run',
              glosses='DET.PL cat-PL run-3PL')

print(example.gloss_list)
# ['DET.PL', '[SEP]', 'cat', 'PL', '[SEP]', 'run', '3PL']
```

## Building

```shell
> pip install -e ".[dev]"
> python -m build
> python3 -m twine upload dist/*
> rm -rf dist
```
