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
 @file distributions.py
 @author Maxim Trokhimtchouk
 @date 13 Feb 2025
"""

import numpy as np
from ..functions.piecewise import linear, constant
from ...extractor import tdigest_merge
from ... import extractor as e
import pandas as pd

class cdf(constant):
    def __init__(self, samples):
        x, count = np.unique(samples, return_counts=True)
        rank = np.cumsum(count)
        y = rank / rank[-1]
        super().__init__(x, y)

class digest:
    def __init__(self, average, count):
        assert len(average) == len(count), 'array of averages and counts must the the same length'
        a = np.array(average)
        c = np.array(count)
        idx = c != 0
        a = a[idx]
        c = c[idx]
        idx = np.argsort(a, kind='stable')
        self.average = a[idx]
        self.count = c[idx]

    def cdf(self):
        x = self.average
        y = self.count
        where = y == 1
        where[0] = False
        insidx = np.arange(start=0, stop=len(x))[where]
        x = np.insert(x, insidx, x[insidx])
        y = np.insert(y, insidx, 0.0)
        charges = (y * (y < 2)) + (y * (y > 1) / 2)
        cumulative = np.roll(y, 1)
        cumulative[0] = 0
        y = np.cumsum(cumulative) + charges
        y = y / y[-1]
        return linear(x, y)

    def quintiles(self):
        return self.cdf().inv()

    def __eq__(self, other):
        return len(self.average) == len(other.average) and \
               (self.average == other.average).all() and \
               (self.count == other.count).all()

    @classmethod
    def merge(self, compression, *dgs):
        res = tdigest_merge(compression, *[{'average': dg.average, 'count': dg.count} for dg in dgs])
        return digest(average=res['average'], count=res['count'])    
    
class digests:
    def __init__(self, frame=None):
        def field_digest(frame, field):
            size = frame.shape[1]
            return [getattr(frame[1, i], field) for i in range(size)], \
                    [getattr(frame[0, i], field) for i in range(size)]
        if isinstance(frame, e.ResultRef) or isinstance(frame, e.Feature):
            self.data = {field: digest(*field_digest(frame, field)) for field in frame.fields()}
        else:
            self.data = {}
            
    def __eq__(self, other):
        if set(self.data.keys()) != set(other.data.keys()):
            return False
        for field in self.data.keys():
            if self.data[field] != other.data[field]:
                return False
        return True

    def __getitem__(self, key) -> digest:
        return self.data[key]

    def quintiles(self) -> dict:
        return {field: digest.quintiles() for field, digest in self.data.items()}

    def cdf(self) -> dict:
        return {field: digest.cdf() for field, digest in self.data.items()}

    @classmethod
    def merge(self, compression, *others):
        assert len(others), 'expect at least one digest to merge'
        fields = set(others[0].data.keys())
        for dgs in others:
            assert fields == set(dgs.data.keys()), "can only add digests with the same fields"
        res = digests()
        for field in fields:
            res.data[field] = digest.merge(compression, *[dg[field] for dg in others])   
        return res

    def write(self, file):
        data = {f: np.array([[a, c] for a, c in zip(d.average, d.count)]).flatten() for f, d in self.data.items()}
        size = max([len(a) for a in data.values()])
        pd.DataFrame(data={f: np.resize(a, size) for f, a in data.items()}).to_pickle(file)

def read_digests(file) -> digests:
    df = pd.read_pickle(file)
    res = digests()
    for field in df.columns:
        res.data[field] = digest(average=df[field][0:-1:2], count=df[field][1::2])
    return res
