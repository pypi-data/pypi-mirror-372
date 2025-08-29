#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-28
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP

"""
A library wrapper around matplotlib for custom plots.
"""



# %% Lazy imports
from corelp import getmodule
__getattr__, __all__ = getmodule(__file__)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)