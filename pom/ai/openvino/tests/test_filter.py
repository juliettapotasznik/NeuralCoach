import pytest
from modules.one_euro_filter import OneEuroFilter, LowPassFilter

class TestLowPassFilter:
    def test_initialization(self):
        lpf = LowPassFilter()
        assert lpf.x_previous is None

    def test_filtering(self):
        lpf = LowPassFilter()
        
        # First value should be returned as is
        val1 = 10.0
        res1 = lpf(val1, alpha=0.5)
        assert res1 == val1
        assert lpf.x_previous == val1
        
        # Second value should be blended
        val2 = 20.0
        res2 = lpf(val2, alpha=0.5)
        # 0.5 * 20 + 0.5 * 10 = 15
        assert res2 == 15.0
        assert lpf.x_previous == 15.0

class TestOneEuroFilter:
    def test_initialization(self):
        oef = OneEuroFilter(freq=30, mincutoff=1.0)
        assert oef.freq == 30
        assert oef.mincutoff == 1.0
        assert oef.x_previous is None
        assert oef.dx is None

    def test_filtering(self):
        oef = OneEuroFilter(freq=30, mincutoff=1.0, beta=0.0)
        
        # First value
        val1 = 10.0
        res1 = oef(val1)
        assert res1 == val1
        
        # Second value
        # With beta=0, it behaves like a simple low pass filter with variable alpha
        # We just check it returns a float and updates state
        val2 = 12.0
        res2 = oef(val2)
        assert isinstance(res2, float)
        assert oef.x_previous == val2
        assert oef.dx is not None
