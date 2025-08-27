"""
Testing utils for ML
"""

from typing import Iterable, Callable, Union, Tuple

import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.base import is_regressor, is_classifier, is_outlier_detector
from sklearn.datasets import make_classification, make_regression
from sklearn.base import BaseEstimator, TransformerMixin
from i2.signatures import call_forgivingly


# ---------------------------------------------------------------------------------------
# Learner equivalence

Learner = BaseEstimator  # but not necessarily fitted
Model = BaseEstimator  # but fitted
Estimator = Union[Callable, str, type, BaseEstimator]
XY = Tuple[Iterable, Iterable]
XYFactory = Callable[[], XY]


def learner_equivalence(
    learner_1, learner_2, xy=None, model_action=None, equivalence_scorer=None
):
    """Returns an score that measures how much the two learners are equivalent.
    The user can specify what data to use (`xy`) to fit the learners,
    what action to take on the fitted model (`model_action`),
    and what function to apply to the two results to compute the final score.

    But the user doesn't HAVE to specify all that usually (if the learners are
    all proper sklearn estimators) -- instead, the function will try to figure
    out defaults for any of these if not given.

    >>> from sklearn.linear_model import LinearRegression as Regressor
    >>> from sklearn.linear_model import RidgeClassifier as Classifier
    >>> from sklearn.decomposition import PCA as UnsupervisedTransformer
    >>>
    >>> from tested.ml import learner_equivalence
    >>>
    >>> for learner in (Regressor, Classifier, UnsupervisedTransformer):
    ...     # assert that a learner is equivalent to itself
    ...     assert learner_equivalence(learner, learner)
    """
    # preprocess inputs
    learner_1 = get_learner(learner_1)
    learner_2 = get_learner(learner_2)
    if xy is None:
        xy = get_xy_factory_for_estimator(learner_1)
    if isinstance(xy, Callable):
        X, y = xy()
    else:
        X, y = xy
    model_action = model_action or learner_1
    model_action, dflt_equivalence_scorer = get_model_action_and_equivalence_scorer(
        model_action
    )
    equivalence_scorer = equivalence_scorer or dflt_equivalence_scorer
    # do the stuff
    learner_1.fit(X, y)
    learner_2.fit(X, y)
    learner_1_output = model_action(learner_1, X)
    learner_2_output = model_action(learner_2, X)
    return equivalence_scorer(learner_1_output, learner_2_output)


def _is_estimator_factory(estimator) -> bool:
    """Tells us if the input might be able to be called to get an estimator"""
    return isinstance(estimator, type) or (
        isinstance(estimator, Callable) and not isinstance(estimator, BaseEstimator)
    )


valid_estimator_kinds = {'classifier', 'regressor', 'transformer'}


def estimator_kind(estimator: Estimator) -> str:
    """Returns the kind (string) of an Estimator"""
    if _is_estimator_factory(estimator):
        estimator = estimator()
    if isinstance(estimator, BaseEstimator):
        if is_classifier(estimator):
            kind = 'classifier'
        elif is_regressor(estimator):
            kind = 'regressor'
        elif TransformerMixin in type(estimator).mro():
            kind = 'transformer'
        else:
            kind = 'regressor'  # we'll just use that for unsupervised?
    elif isinstance(estimator, str):
        kind = estimator
    else:
        raise ValueError(f"Couldn't result estimator to a kind: {estimator}")
    return kind


def get_xy_factory_for_estimator(estimator: Estimator) -> XYFactory:
    kind = estimator_kind(estimator)

    if isinstance(kind, str):
        data_generators = {
            'classifier': make_classification,
            'regressor': make_regression,
            'transformer': make_regression,  # or classification better?
        }
        data_gen = data_generators.get(kind, None)
        if data_gen is None:
            raise ValueError(f'A string estimator must be one of {data_generators}')
    elif isinstance(kind, Callable):
        data_gen = kind
    else:
        raise ValueError(f'Unrecognized kind of estimator: {estimator}')
    return data_gen


def get_learner(learner) -> Learner:
    if isinstance(learner, type):
        # TODO: Do this for any Callable? (Need distinguish with callable instance)
        learner = learner()
    return learner


def get_model_action_and_equivalence_scorer(model_action):
    """Returns a default (model_action, equivalence_scorer) for a given model_action
    It will return the model_action as is if not a learner.
    If a learner, it will try to figure out a default model_action for it.
    """
    if isinstance(model_action, Learner):
        learner = model_action
        _estimator_kind = estimator_kind(learner)
        return {
            'classifier': (lambda model, X: getattr(model, 'predict')(X), np.allclose,),
            'regressor': (lambda model, X: getattr(model, 'predict')(X), np.allclose),
            'transformer': (
                lambda model, X: getattr(model, 'transform')(X),
                np.allclose,
            ),
        }.get(_estimator_kind)
    else:
        return model_action, np.allclose


# ---------------------------------------------------------------------------------------
# Train-test splits


def keys_aligned_list(iterable_spec, keys):
    """Get an iterable that is aligned with the keys iterable, and verify that it is so.

    >>> keys_aligned_list(lambda x: x * 2, keys=[1, 2, 3])
    [2, 4, 6]
    >>> keys_aligned_list([2, 4, 6], keys=[1, 2, 3])
    [2, 4, 6]
    >>> assert keys_aligned_list(None, keys=[1, 2, 3]) is None

    :param iterable_spec:
    :param keys:
    :return:
    """
    if iterable_spec is None:
        return None
    elif isinstance(iterable_spec, Callable):
        return list(map(iterable_spec, keys))
    elif isinstance(iterable_spec, Iterable):
        iterable_spec = list(iterable_spec)
        assert len(iterable_spec) == len(keys)
        return iterable_spec
    else:
        raise TypeError(
            f'Unknown iterable_spec type ({type(iterable_spec)}): {iterable_spec}'
        )


def train_test_split_keys(
    keys: Iterable,
    key_to_tag: Union[Callable, Iterable, None] = None,
    key_to_group: Union[Callable, Iterable, None] = None,
    *,
    # Yes, these are used, but lint doesn't see it because using locals() to get them
    test_size=None,
    train_size=None,
    random_state=None,
    n_splits=1,
):
    """Split keys into train and test lists.

    The ``train_keys`` and ``test_keys`` are disjoint and taken from ``keys``.

    Specifying ``key_to_tag`` (a function or iterable) ensures that ``tags`` will be
    well distributed in both train and test.

    Specifying ``key_to_group`` (a function or iterable) ensures **on the contrary**
    that keys of a same group will be entirely in train **or (exclusive)** in
    test -- not both.

    :param keys: keys to be split
    :param key_to_tag: keys-aligned iterable of tags (a.k.a y/classes in
        sklearn speak) or function to compute these from keys
    :param key_to_group: keys-aligned iterable of groups or function to compute
        these from keys
    :return a ``(train_keys, test_keys)`` pair (all elements of keys) if ``n_splits=1``,
        and a generator of such pairs if not.

    Note that in the doctest below, we take ``keys=[7, 14, 21, ...]`` to show that
    it's not about ``[0, 1, 2, ...]`` indices only, but ANY keys
    (even non numerical -- like filepaths, DB selectors, etc.)

    >>> keys = range(7, 7 + 100 * 7, 7)  # [7, 14, 21, ..., 700]
    >>> def mod5(x):
    ...     return x % 5
    >>> train_keys, test_keys = train_test_split_keys(keys, key_to_group=mod5,
    ...     train_size=.5, random_state=42)

    Observe here that though ``train_size=.5``, the proportion is not 50/50.
    That's because the group constraint, imposed by the key_to_group argument
    produces only 5 groups.

    >>> len(train_keys), len(test_keys)
    (40, 60)

    But especially, see that though there's a lot of train and test indices,
    within train, there's only 2 unique groups (all 0 or 3 modulo 5)
    and only 3 unique groups (1, 2, 4 modulo 5) within test indices.

    >>> assert set(map(mod5, train_keys)) == {0, 3}
    >>> assert set(map(mod5, test_keys)) == {1, 2, 4}

    """
    splitter = call_forgivingly(
        GroupShuffleSplit, **locals()
    )  # calls GroupShuffleSplit on relevant inputs

    keys = np.array(list(keys))
    y = keys_aligned_list(key_to_tag, keys)
    groups = keys_aligned_list(key_to_group, keys)
    if groups is None:
        groups = range(len(keys))

    n = splitter.get_n_splits(keys, y, groups)
    if n == 1:
        train_idx, test_idx = next(splitter.split(keys, y, groups))
        return keys[train_idx], keys[test_idx]
    else:

        def gen():
            for train_idx, test_idx in splitter.split(keys, y, groups):
                yield keys[train_idx], keys[test_idx]

        return gen()
