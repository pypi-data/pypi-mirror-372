"""
        COPYRIGHT (c) 2025 by Featuremine Corporation.
        This software has been provided pursuant to a License Agreement
        containing restrictions on its use.  This software contains
        valuable trade secrets and proprietary information of
        Featuremine Corporation and is protected by law.  It may not be
        copied or distributed in any form or medium, disclosed to third
        parties, reverse engineered or used in any manner not provided
        for in said License Agreement except with the prior written
        authorization from Featuremine Corporation.

        """
"""
 @file piecewise.py
 @author Maxim Trokhimtchouk
 @date 13 Feb 2025
"""

import numpy as np

class linear:
    def __init__(self, x, y):
        x = np.array(x)
        y = np.array(y)
        idx = np.argsort(x, kind='stable')
        self.x = x[idx]
        self.y = y[idx]

    def __call__(self, xs):
        singleton = isinstance(xs, float)
        xs = [xs] if singleton else xs
        res = np.interp(xs, self.x, self.y)
        return res[0] if singleton else res

    def inv(self):
        return linear(self.y, self.x)

class constant:
    def __init__(self, x, y):
        x = np.array(x)
        y = np.array(y)
        idx = np.argsort(x, kind='stable')
        self.x = x[idx]
        self.y = y[idx]

    def __call__(self, xs):
        singleton = isinstance(xs, float)
        xs = [xs] if singleton else xs
        idx = np.searchsorted(self.x, xs, side='right')
        idx = np.clip(idx - 1, 0, len(self.x) - 1)
        res = self.y[idx]
        return res[0] if singleton else res

    def inv(self):
        return linear(self.y, self.x)
