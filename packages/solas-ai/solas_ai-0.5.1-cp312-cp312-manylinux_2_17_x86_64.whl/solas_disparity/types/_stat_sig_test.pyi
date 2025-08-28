from ._enum_base import EnumBase as EnumBase

class StatSigTest(EnumBase):
    FISHERS_OR_CHI_SQUARED = 'fishers_or_chi_squared'
    FISHERS_EXACT = 'fishers_exact'
    CHI_SQUARED_TEST = 'chi_squared_test'
    TWO_SAMPLE_T_TEST = 'two_sample_t_test'
    STACKED_REGRESSION = 'stacked_regression'
    BOOTSTRAPPING = 'bootstrapping'
