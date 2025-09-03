"""
Describe purpose of this script here

Created: 8/28/25
"""
import pytest

from magrathea.triangle.meshload import load3mf

@pytest.mark.parametrize(
    "inf",["data/output/mesh/voyager.3mf",
    "data/output/mesh/cube.3mf"]
)
def test_3mf(inf):
    mesh=load3mf(inf)
