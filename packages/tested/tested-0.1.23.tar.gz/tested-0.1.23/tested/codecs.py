"""Tools to test codecs -- i.e. serialization/deserialization pairs

`validate_codec`: a function to test encoder/decoder pairs.

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
import pickle


def return_object_itself(obj):
    return obj


def always_true(obj, decoded_obj):
    return True


def encode_and_decode(obj, coder=pickle.dumps, decoder=pickle.loads):
    encoded_obj = coder(obj)
    decoded_obj = decoder(encoded_obj)
    return decoded_obj


# TODO: Add doctests using caught_errors
# TODO: Discuss how the validate_codec can also solve decoding in a different env or
#  location
def validate_codec(
    obj,
    coder=pickle.dumps,
    decoder=pickle.loads,
    command=return_object_itself,
    comparison=always_true,
    caught_errors=(Exception,),
):
    """Validate a coder/decoder pair.

    Encodes the input `obj` with `coder`, then `decodes` the encoded object,
    returning `comparison(command(obj), command(decoded_obj))`.
    If an exception is raised, that is caught by `caught_errors`, `False` will be
    returned.

    :param obj: Object that should be serialized/encoded then deserialized/decoded
    :param coder: The serializer.
    :param decoder: The deserializer.
    :param command: Function to apply to both obj and decoded_obj before comparing
    :param comparison: Function that will be called on (obj, decoded_obj)
    :param caught_errors: The exception types to catch (and return False)
    :return: Whatever comparison returns

    Note: The `command` function is not necessary since a custom comparison function
    could be made to apply such a function to the obj and decoded_obj before comparing.
    We provide command though, because it allows the user to set a comparison function,
    but vary what is being compared.
    For instance, we may want to use `==` (i.e. `operator.eq`) as our comparison
    function, but apply this not to the objects themselves, but to some results
    of operating with or on them.
    For example, say you may not want to compare `func == decoded_func`, but instead
    `func(42) == decoded_func(42)`.
    In that case, you would specify `command=lambda f: f(42)`.

    To demo how `validate_codec` works, we'll import two classes, and print their
    code below. The reason we don't define them inline is because pickle can't
    be used inside a module where the type of the object to pickle is defined.

    >>> from tested.tests.objects_for_testing import A, B
    >>> import inspect
    >>> print(inspect.getsource(A))
    class A:
        def __init__(self, x):
            self.x = x
    <BLANKLINE>
        def __add__(self, other):
            return self.x + other
    <BLANKLINE>
    >>> print(inspect.getsource(B))
    class B(A):
        def __eq__(self, other):
            return self.x == other.x
    <BLANKLINE>

    Let's make a few objects to test with:

    >>> a_list = [1,2,3]
    >>> a_tuple = (1, 2, 3)
    >>> a = A(42)
    >>> b = B(42)

    Out-of-the-box, the only thing that `validate_codec` validates, is the ability of
    a coder/decoder pair to serialize, then deserialize an object.

    >>> assert validate_codec(a_list)
    >>> assert validate_codec(a)

    The default `coder` and `decoder` are `pickle.dumps` and `pickle.loads`
    respectively, so you wouldn't be able to pickle a lambda function, for instance:

    >>> assert not validate_codec(lambda x: x)

    The real usage of `validate_codec` though is to use `functools.partial` to fix the
    arguments to those that make sense for the codec and objects to be coded and decoded.

    Say for example, that we want to use equality `==` to compare the original object
    with the decoded one. In that case, we'd do this:

    >>> from functools import partial
    >>> from operator import eq
    >>>
    >>> equality_validator = partial(validate_codec, comparison=eq)
    >>> assert equality_validator(a_list)
    >>> assert not equality_validator(a)
    >>> assert equality_validator(b)

    The instance `a` of `A` didn't pass validation because by default, python objects
    compare on the basis of their `id`, which is a low level unique reference (
    integer) of an object.
    It worked with `a_list` and with `b` because these have their own definition of
    equality that bipasses `id`.

    If we wanted to force the comparison based on `id` anyway, we could do it like this:

    >>> id_equality_validator = partial(validate_codec, command=id, comparison=eq)
    >>> assert not id_equality_validator(a_list)
    >>> assert not id_equality_validator(a)
    >>> assert not id_equality_validator(b)

    The `id`-based comparison above was just meant for illustration.
    I can't think of any use case where it would be useful.
    On the other hand, the `command` argument has it's uses.

    Here is now the crux of the matter: Functional equivalence.

    No matter what anyone tells you, objects are useless in and of themselves.
    It's their use, their behavior, that matters.
    Therefore, when you decode an object, you're not really looking for the exact
    same object that was encoded.
    We've seen that in fact, from the point of view of low level concerns such as
    the `id`, you'll never get the exact same object.
    What you should expect to get though, is some equivalence from the behavior point
    of view.
    That is, you need to be able to rely on getting "the same" results when operating
    with the decoded object.

    This is where `command` and `comparison` come in.

    `command` specifies what operation(s) you want to be able to do on the decoded
    object, and `comparison` specifies how you compare the results of carrying out
    those same operations on the original object and the decoded one.

    Note that `A` (and therefore `B`) have been defined so that we can sum instances
    with a number:

    >>> a + 1
    43

    If what I really want out of my `A` and `B` instances is to add a number to it,
    I can validate that like so:

    >>> equivalence_validator = partial(
    ...     validate_codec,
    ...     command=lambda obj: obj + 1,
    ...     comparison=eq
    ... )
    >>> assert equivalence_validator(a)
    >>> assert equivalence_validator(b)


    So far, we've only used the default `pickle` encoder and decoders.
    Let's try out another pair.

    >>> import array
    >>> import struct
    >>> from functools import partial
    >>>
    >>> def float_encoder(a):
    ...     return struct.pack(len(a) * 'f', *a)
    ...
    >>> def float_decoder(b):
    ...     n = struct.calcsize('f')
    ...     return list(struct.unpack(int(len(b) / n) * 'f', b))
    >>>
    >>> a_list = [1, 2, 3]
    >>> a_tuple = (1, 2, 3)
    >>> an_array_of_floats = array.ArrayType('f', [1 / 100, 100])
    >>> an_array_of_doubles = array.ArrayType('d', [1 / 100, 100])
    >>>
    >>> float_validator = partial(
    ...     validate_codec,
    ...     coder=float_encoder,
    ...     decoder=float_decoder,
    ...     comparison=eq
    ... )
    >>>
    >>> assert float_validator(a_list)
    >>> assert not float_validator(a_tuple)
    >>> assert not float_validator(an_array_of_floats)

    The reason why `a_tuple` and `an_array_of_floats` don't validate is because
    array_codec decodes all iterables as lists, which are then compared to
    a tuple and an array (different types)
    Instead of using eq here, we should compare all elements individually:

    >>> all_equal = lambda x, y: all(xi == yi for xi, yi in zip(x, y))
    >>> float_validator_2 = partial(float_validator, comparison=all_equal)
    >>> assert float_validator_2(a_list)
    >>> assert float_validator_2(a_tuple)
    >>> assert float_validator_2(an_array_of_floats)
    >>> # but...
    >>> assert not float_validator_2(an_array_of_doubles)

    Why?
    Because we're using 'f' formatting spec, which is a float with 4 bytes
    yet the array is uses 'd' formatting (for doubles)
    It's easy to get into a... pickle of comparison comparing floats to doubles.
    We should probably use math.isclose to compare instead...

    >>> import math
    >>> all_are_close = lambda x, y: all(
    ...     math.isclose(xx, yy, rel_tol=1e-6) for xx, yy in zip(x, y)
    ... )
    >>>
    >>> float_validator_3 = partial(float_validator, comparison=all_are_close)
    >>> assert float_validator_3(a_list)
    >>> assert float_validator_3(a_tuple)
    >>> assert float_validator_3(an_array_of_floats)
    >>> assert float_validator_3(an_array_of_doubles)  # works with doubles now!

    """
    try:
        decoded_obj = encode_and_decode(obj, coder, decoder)
        obj_result = command(obj)
        decoded_obj_result = command(decoded_obj)
        return comparison(obj_result, decoded_obj_result)
    except caught_errors:
        return False
