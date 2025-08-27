"""General python testing utils

A little tour...

Let's start with `validate_codec`, a function to test encoder/decoder pairs.

>>> from tested import validate_codec

`pickle.dumps/pickle.loads` is the default encoder/decoder pair.
You can pickle lists, and datetime objects

>>> validate_codec([1, 2, 3])
True
>>> from datetime import datetime
>>> validate_codec(datetime.now())
True

But you can't pickle a lambda function

>>> validate_codec(lambda x: x)
False

>>> from functools import partial
>>> import json
>>> validate_jsonability = partial(validate_codec, coder=json.dumps, decoder=json.loads)

You can jsonize lists and dicts

>>> assert validate_jsonability([1, 2, 3])
>>> assert validate_jsonability({'a': 1, 'b': {'c': [1, 2, 3]}})

You can't jsonize datetime objects

>>> from datetime import datetime
>>> validate_jsonability(datetime.now())
False

See `validate_codec` docs for more examples.

"""

from tested.multiple import run_multiple_pytests
from tested.ml import train_test_split_keys, learner_equivalence
from tested.codecs import encode_and_decode, validate_codec
