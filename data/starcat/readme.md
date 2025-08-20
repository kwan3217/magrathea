* Yale Bright Star Catalog - Catalog of about
  9,000 stars, complete to about Vmag 6.5.
  This represents all naked-eye visible stars.
  - [VizieR entry](https://cdsarc.cds.unistra.fr/viz-bin/cat/V/50)
  - [Readme for catalog](https://cdsarc.cds.unistra.fr/ftp/V/50/ReadMe)
  - [catalog.gz](https://cdsarc.cds.unistra.fr/ftp/V/50/catalog.gz) 
    Code should use this compressed version
    directly, with the standard gzip module.
* [Augmented Tycho+Hipparcos+Yale+Gilese](https://codeberg.org/astronexus/athyg) - composite catalog with the best of all worlds. The
  main catalog has about 2.5M stars, based on Tycho but with the best data
  from all catalogs. Generally positions are from Hipparcos-2 and distances are
  from Gaia DR3.
  - [athyg_33_reduced_m10.csv.gz](https://codeberg.org/astronexus/athyg/src/branch/main/data/subsets/athyg_33_reduced_m10.csv.gz) 
    This has all stars with M<10 and all stars within 100 light years.
  
  Format is CSV
  *  id - primary key
  * tyc - Tycho-2 catalog foreign key
  * gaia - Gaia DR3 foreign key
  * hyg - older HYG catalog foreign key (not useful to us)
  * hd - Bright star catalog foreign key
  * gl
  * bayer - Bayer greek letter
  * flam - Flamsteed number
  * con - Constellation. bayer+con is Bayer designation IE Alpha Centauri
  * proper - proper name
  * ra - right ascension in hours
  * dec - declination in degrees
  * pos_src (none of the bright stars are from Gaia or GJ)
    * T - Tycho
    * HIP_X - Hipparcos
  * dist - distance in parsecs
  * x0,y0,z0 - 3D coordinates in parsecs
  * dist_src
    * HIP - Hipparcos
    * G_R3 - Gaia DR3
  * mag - magnitude
  * absmag - absolute magnitude