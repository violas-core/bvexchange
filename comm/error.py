#!/usr/bin/python3

import sys
from enum import Enum
name="error"
class error(Enum):
    SUCCEED = "succeed"
    FAILED  = "failed"
    EXCEPT  = "except"
    ARG_INVALID = "argument invalid"


