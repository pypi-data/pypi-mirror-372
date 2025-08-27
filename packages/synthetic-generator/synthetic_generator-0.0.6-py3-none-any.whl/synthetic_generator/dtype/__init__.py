from .base import *
from .float import *
from .int import *

#@formatter:off
base_type = BaseType()
base_float = BaseFloat()
base_int = BaseInt()
# Float
float_type = FloatType()
# Int
int_type = IntType()
#@formatter:on

__all__ = [
    ##### Classes #####
    # Base
    'BaseType',
    'BaseFloat',
    'BaseInt',
    # Float
    'FloatType',
    # Int
    'IntType',
    ##### Instances #####
    # Base
    'base_type',
    'base_float',
    'base_int',
    # Float
    'float_type',
    # Int
    'int_type',
]
