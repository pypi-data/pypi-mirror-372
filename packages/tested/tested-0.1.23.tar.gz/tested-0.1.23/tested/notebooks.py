"""Tools for testing with notebooks.

We often test our stuff somewhere in a notebook.

Since we already spent time doing that, how can we get more out of the investment
by making our work more reusable?

Ideas.

Gather the relevant cells and generate a string that can be pasted into a test
 module/function. Problems:
- Getting the right environment (imports, data, etc.)
- asserting (can use out cells sometimes, but sometimes harder)

For doctests? Change comments to markdown text and code to doctests.

Links to check out:
- https://semaphoreci.com/blog/test-jupyter-notebooks-with-pytest-and-nbmake

"""

from itertools import starmap
from typing import Iterable, Any


class CellFuncs:
    """A collection of cell funcs to use with InOut.cells_2_str"""

    @staticmethod
    def out_as_comment(in_, out_, prefix='# Out: '):
        """Insert out_ cell as comment after in_"""
        if out_ is not None:
            out_str = str(out_)
            if '\n' not in out_str:
                out_str = prefix + out_str
            else:
                out_str = (
                    prefix + '\n' + '\n'.join(('# ' + x for x in out_str.split('\n')))
                )
            return in_ + '\n' + out_str
        else:
            return in_

    @staticmethod
    def assertion_when_it_works(
        in_,
        out_,
        fallback=lambda in_, out_: in_,  # just return None
        globals_=None,
        locals_=None,
    ):
        r"""
        >>> CellFuncs.assertion_when_it_works("3 + 4", 7)
        'assert (3 + 4) == (7)\n'
        >>> CellFuncs.assertion_when_it_works("dict(a=1, b=2)", {'a': 1, 'b': 2})
        "assert (dict(a=1, b=2)) == ({'a': 1, 'b': 2})\n"

        And if the left and right are not equal when evaluated,
        by default (fallback) just the in_ is returned

        >>> CellFuncs.assertion_when_it_works("dict(a=1, b=2)", "is not equal to this")
        'dict(a=1, b=2)'

        """
        if out_ is not None:
            command = f'({in_}) == ({out_})\n'
            try:
                bool_ = eval(command, globals_, locals_)
            except Exception:
                bool_ = False
            if bool_:
                return f'assert {command}'
            else:
                return fallback(in_, out_)
        else:
            return in_


InCell = str
OutCell = Any

from typing import Protocol, runtime_checkable
from i2 import Sig


@runtime_checkable
class InCellFilter(Protocol):
    def __call__(self, in_cell: str) -> bool:
        pass


@runtime_checkable
class InOutCellFilter(Protocol):
    def __call__(self, in_cell: str, out_cell: Any) -> bool:
        pass


class InOut:
    """Get (in, out) pairs of cell contents.

    In a notebook, do:
    ```
    t = InOut(In, Out)
    ```

    `In` and `Out` are automatically available in a notebook.

    Now you can access (in, out) pairs with `t[k]` where `k` can be an integer, a slice,
    or a list/iterable of integers, or a (in, or (in, out) filter) function.

    Examples:

    ```
    t[4]  # the (in, out) cell for idx=4

    print(t.cells_2_str(t[10:20])

    print(t.cells_2_str(t[[77, 86, 99, 87, 89]],
            cell_func=CellFuncs.assertion_when_it_works))

    # number of in_ cells that have exactly one line
    len(t[lambda in_: len(in_.split('\n')) == 1])

    # number of out cells that are not None
    len(t[lambda in_, out_: out_ is not None])
    ```

    """

    def __init__(self, In, Out):
        self.In = In
        self.Out = Out

    def __getitem__(self, k):
        if isinstance(k, int):
            return self.In[k], self.Out[k]
        else:
            return [
                (self.In[idx], self.Out[idx] if idx in self.Out else None)
                for idx in self.idx_gen(k)
            ]

    def _in_out_pairs_with_sentinel_out_when_missing(self, sentinel=None):
        for i, in_ in enumerate(self.In):
            if i in self.Out:
                yield in_, self.Out[i]
            else:
                yield in_, sentinel

    def idx_gen(self, k):
        if isinstance(k, int):
            yield k
        elif isinstance(k, slice):
            yield from range(k.start, k.stop, k.step or 1)
        elif isinstance(k, (InCellFilter, InOutCellFilter)):
            # Note, the above ininstance check is just a "is callable" check!
            n_required_args = Sig(k).n_required
            if n_required_args == 1:
                in_filt = k
                yield from (i for i, in_ in enumerate(self.In) if in_filt(in_))
            elif n_required_args == 2:
                in_out_filt = k
                in_outs = self._in_out_pairs_with_sentinel_out_when_missing()
                yield from (
                    i for i, (in_, out_) in enumerate(in_outs) if in_out_filt(in_, out_)
                )
            else:
                raise ValueError(f'A cell filter must have 1 or 2 required arguments')
        elif isinstance(k, Iterable):
            yield from k

    def index_has_an_in(self, idx):
        return idx in self.In

    @staticmethod
    def cells_2_str(cells_list, cell_func=CellFuncs.out_as_comment, sep='\n'):
        """Get a string out of a list of cells.
        Probably the main utility of InOut.
        """
        return sep.join(starmap(cell_func, cells_list))

    @classmethod
    def from_locals(cls, _locals):
        """A convenience function to get an InOut.

        Pretty much only one way to call it, from your notebook, do this:

        ```
        t = InOut(locals())
        ```

        """
        return cls(_locals['In'], _locals['Out'])
