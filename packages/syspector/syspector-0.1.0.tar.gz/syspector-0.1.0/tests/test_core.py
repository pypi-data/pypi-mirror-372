import pytest
from syspector.core import SystemInspector

def test_snapshot_structure():
    s = SystemInspector().snapshot()
    assert hasattr(s, 'cpu_percent')
    assert hasattr(s, 'mem_total')
    assert isinstance(s.cpu_count, int)
