"""
Describe purpose of this script here

Created: 8/20/25
"""
from magrathea import load_stars


def test_load_stars():
    stars=load_stars()
    print(len(stars))