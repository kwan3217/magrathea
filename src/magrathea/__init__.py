"""
Magrathea: A library for synthesizing planetary and space imagery.

Inspired by James Blinn's Voyager animations, this package provides functions to render planets, stars, rings,
and spacecraft using NumPy, SPICE kernels, and texture maps.

Main functions:
- draw_planet, draw_planets: Renders planetary surfaces.
- draw_stars: Adds starfields to scenes.
- rings: Generates planetary ring systems.
- triangles: Draws spacecraft models.

Created: 8/19/25
"""

from .planet import draw_planet, draw_planets
from .stage import stage
from .stars.starcat import load_stars
from .stars.stardraw import draw_stars

