from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Define the Cython extension module
ext_modules = [
    Extension(
        name="magrathea.planet.draw_planet_bottom_cy",
        sources=[
            "src/magrathea/planet/draw_planet_bottom_cy.pyx",
            "src/magrathea/planet/draw_planet_bottom.c",
            "src/magrathea/planet/shadow.c"
        ],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3"]
    ),
    Extension(
        name="magrathea.triangle.tridraw_cy",
        sources=[
            "src/magrathea/triangle/tridraw_cy.pyx",
            "src/magrathea/triangle/tridraw.c"
        ],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3"]
    )
]

setup(
    ext_modules=cythonize(ext_modules, language_level=3)
)