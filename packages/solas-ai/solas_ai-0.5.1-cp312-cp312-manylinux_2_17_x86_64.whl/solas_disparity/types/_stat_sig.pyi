import attr
import pandas as pd
from ._stat_sig_test import StatSigTest as StatSigTest
from _typeshed import Incomplete
from solas_disparity.utils import compare_pandas_objects as compare_pandas_objects

@attr.define(auto_attribs=True)
class StatSig:
    stat_sig_test: StatSigTest = attr.field(init=True)
    summary_table: pd.DataFrame = attr.field(init=True, factory=Incomplete, eq=attr.cmp_using(compare_pandas_objects))
