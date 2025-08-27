# tested
General python testing utils

To install:	```pip install tested```


# A little tour...

## validate_codec

Let's start with `validate_codec`, a function to test encoder/decoder pairs.

```python
>>> from tested import validate_codec
```

`pickle.dumps/pickle.loads` is the default encoder/decoder pair.
You can pickle lists, and datetime objects

```python
>>> validate_codec([1, 2, 3])
True
>>> from datetime import datetime
>>> validate_codec(datetime.now())
True
```

But you can't pickle a lambda function

```python
>>> validate_codec(lambda x: x)
False
>>> from functools import partial
>>> import json
>>> validate_jsonability = partial(validate_codec, coder=json.dumps, decoder=json.loads)
```

You can jsonize lists and dicts

```python
>>> assert validate_jsonability([1, 2, 3])
>>> assert validate_jsonability({'a': 1, 'b': {'c': [1, 2, 3]}})
```

You can't jsonize datetime objects

```python
>>> from datetime import datetime
>>> validate_jsonability(datetime.now())
False
```

See [`validate_codec` docs](https://i2mint.github.io/tested/module_docs/tested/codecs.html#tested.codecs.validate_codec)
for more examples.

