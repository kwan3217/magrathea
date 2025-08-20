"""
Bright star catalog, sorted by brightness.

Byte-by-byte Description of file: catalog.dat
Stars are fields we care about
--------------------------------------------------------------------------------
   Bytes Format  Units     Label      Explanations
--------------------------------------------------------------------------------
   1-  4  I4     ---       HR         [1/9110]+ Harvard Revised Number
                                      = Bright Star Number
   5- 14  A10    ---       Name       Name, generally Bayer and/or Flamsteed name
  15- 25  A11    ---       DM         Durchmusterung Identification (zone in
                                      bytes 17-19)
  26- 31  I6     ---       HD         [1/225300]? Henry Draper Catalog Number
  32- 37  I6     ---       SAO        [1/258997]? SAO Catalog Number
  38- 41  I4     ---       FK5        ? FK5 star Number
      42  A1     ---       IRflag     [I] I if infrared source
      43  A1     ---       r_IRflag  *[ ':] Coded reference for infrared source
      44  A1     ---       Multiple  *[AWDIRS] Double or multiple-star code
  45- 49  A5     ---       ADS        Aitken's Double Star Catalog (ADS) designation
  50- 51  A2     ---       ADScomp    ADS number components
  52- 60  A9     ---       VarID      Variable star identification
  61- 62  I2     h         RAh1900    ?Hours RA, equinox B1900, epoch 1900.0 (1)
  63- 64  I2     min       RAm1900    ?Minutes RA, equinox B1900, epoch 1900.0 (1)
  65- 68  F4.1   s         RAs1900    ?Seconds RA, equinox B1900, epoch 1900.0 (1)
      69  A1     ---       DE-1900    ?Sign Dec, equinox B1900, epoch 1900.0 (1)
  70- 71  I2     deg       DEd1900    ?Degrees Dec, equinox B1900, epoch 1900.0 (1)
  72- 73  I2     arcmin    DEm1900    ?Minutes Dec, equinox B1900, epoch 1900.0 (1)
  74- 75  I2     arcsec    DEs1900    ?Seconds Dec, equinox B1900, epoch 1900.0 (1)
* 76- 77  I2     h         RAh        ?Hours RA, equinox J2000, epoch 2000.0 (1)
* 78- 79  I2     min       RAm        ?Minutes RA, equinox J2000, epoch 2000.0 (1)
* 80- 83  F4.1   s         RAs        ?Seconds RA, equinox J2000, epoch 2000.0 (1)
*     84  A1     ---       DE-        ?Sign Dec, equinox J2000, epoch 2000.0 (1)
* 85- 86  I2     deg       DEd        ?Degrees Dec, equinox J2000, epoch 2000.0 (1)
* 87- 88  I2     arcmin    DEm        ?Minutes Dec, equinox J2000, epoch 2000.0 (1)
* 89- 90  I2     arcsec    DEs        ?Seconds Dec, equinox J2000, epoch 2000.0 (1)
  91- 96  F6.2   deg       GLON       ?Galactic longitude (1)
  97-102  F6.2   deg       GLAT       ?Galactic latitude (1)
*103-107  F5.2   mag       Vmag       ?Visual magnitude (1)
     108  A1     ---       n_Vmag    *[ HR] Visual magnitude code
     109  A1     ---       u_Vmag     [ :?] Uncertainty flag on V
 110-114  F5.2   mag       B-V        ? B-V color in the UBV system
     115  A1     ---       u_B-V      [ :?] Uncertainty flag on B-V
 116-120  F5.2   mag       U-B        ? U-B color in the UBV system
     121  A1     ---       u_U-B      [ :?] Uncertainty flag on U-B
 122-126  F5.2   mag       R-I        ? R-I   in system specified by n_R-I
     127  A1     ---       n_R-I      [CE:?D] Code for R-I system (Cousin, Eggen)
*128-147  A20    ---       SpType     Spectral type
     148  A1     ---       n_SpType   [evt] Spectral type code
 149-154  F6.3   arcsec/yr pmRA       ?Annual proper motion in RA J2000, FK5 system
 155-160  F6.3   arcsec/yr pmDE       ?Annual proper motion in Dec J2000, FK5 system
     161  A1     ---       n_Parallax [D] D indicates a dynamical parallax,
                                      otherwise a trigonometric parallax
 162-166  F5.3   arcsec    Parallax   ? Trigonometric parallax (unless n_Parallax)
 167-170  I4     km/s      RadVel     ? Heliocentric Radial Velocity
 171-174  A4     ---       n_RadVel  *[V?SB123O ] Radial velocity comments
 175-176  A2     ---       l_RotVel   [<=> ] Rotational velocity limit characters
 177-179  I3     km/s      RotVel     ? Rotational velocity, star_vec sin i
     180  A1     ---       u_RotVel   [ :star_vec] uncertainty and variability flag on
                                      RotVel
 181-184  F4.1   mag       Dmag       ? Magnitude difference of double,
                                        or brightest multiple
 185-190  F6.1   arcsec    Sep        ? Separation of components in Dmag
                                        if occultation binary.
 191-194  A4     ---       MultID     Identifications of components in Dmag
 195-196  I2     ---       MultCnt    ? Number of components assigned to a multiple
     197  A1     ---       NoteFlag   [*] a star indicates that there is a note
                                        (file notes.dat)
--------------------------------------------------------------------------------

Created: 8/19/25
"""

import gzip

import numpy as np
from kwanmath.geodesy import llr2xyz
from kwanmath.interp import linterp
from spiceypy import pxform


def _get_ra(s):
    """
    :param N: Star index in brightness order
    :return: Right Ascension in degrees
    """
    # * 76- 77  I2     h         RAh        ?Hours RA, equinox J2000, epoch 2000.0 (1)
    # * 78- 79  I2     min       RAm        ?Minutes RA, equinox J2000, epoch 2000.0 (1)
    # * 80- 83  F4.1   s         RAs        ?Seconds RA, equinox J2000, epoch 2000.0 (1)
    hours=float(s[76 - 1:77])
    minutes=float(s[78 - 1:79])
    seconds=float(s[80 - 1:83])
    return (hours+minutes/60+seconds/3600)*15


def _get_dec(s):
    """
    :param N: Star index in brightness order
    :return: Declination in degrees
    """
    # *     84  A1     ---       DE-        ?Sign Dec, equinox J2000, epoch 2000.0 (1)
    # * 85- 86  I2     deg       DEd        ?Degrees Dec, equinox J2000, epoch 2000.0 (1)
    # * 87- 88  I2     arcmin    DEm        ?Minutes Dec, equinox J2000, epoch 2000.0 (1)
    # * 89- 90  I2     arcsec    DEs        ?Seconds Dec, equinox J2000, epoch 2000.0 (1)
    sign   = s[84 - 1:84]
    degrees=float(s[85 - 1:86])
    minutes=float(s[87 - 1:88])
    seconds=float(s[89 - 1:90])
    return (degrees+minutes/60+seconds/3600)*(-1 if sign=="-" else 1)


def _get_mag(s):
    """
    :param N: Star index in brightness order
    :return: Magnitude, lower number is brighter
    """
    #*103-107  F5.2   mag       Vmag       ?Visual magnitude (1)
    return float(s[103 - 1:107])


def _get_name(s):
    """
    :param N: Star index in brightness order
    :return: Bayer designation, Flamsteed designation, or both, followed by HR number
    """
    #   1-  4  I4     ---       HR         [1/9110]+ Harvard Revised Number
    #                                      = Bright Star Number
    #   5- 14  A10    ---       Name       Name, generally Bayer and/or Flamsteed name
    return s[5 - 1:14]+ " HR"+ s[1 - 1:4]


def _get_spectral_letter(s):
    """
    :param N: Star index in brightness order
    :return: Spectral class letter, one of OBAFGKM
    """
    #*128-147  A20    ---       SpType     Spectral type
    return s[130 - 1:130]


def _get_spectral_subtype(s):
    """
    :param N: Star index in brightness order
    :return: Spectral subtype from 0 (hottest) to 9 (coolest). 10 would equivalent to 0 of the next cooler class.
    """
    #*128-147  A20    ---       SpType     Spectral type
    try:
        return float(s[131 - 1:131])
    except ValueError:
        # Don't try to parse the more complicated spectral types
        return 5.0


def _get_spectral_type(s):
    #Returns number corresponding to spectral type, O=zero, M=6
    spectral_letter=_get_spectral_letter(s)
    if spectral_letter=="O" or spectral_letter=="W":
        return 0
    elif spectral_letter=="B":
        return 1
    elif spectral_letter=="A":
        return 2
    elif spectral_letter=="F":
        return 3
    elif spectral_letter=="G":
        return 4
    elif spectral_letter=="K" or spectral_letter=="R" or spectral_letter=="S":
        return 5
    elif spectral_letter=="M" or spectral_letter=="N" or spectral_letter=="C":
        return 6


_spectral_letter_colors=[ #Note that these are symbolic colors, not actual colors from the blackbody curve.
    np.array((0.5 ,0.5 ,1  )), #O,W
    np.array((0.75,0.75,1  )), #B
    np.array((1   ,1   ,1  )), #A
    np.array((1   ,1   ,0.5)), #F
    np.array((1   ,1   ,0  )), #G
    np.array((1   ,0.5 ,0  )), #K,R,s
    np.array((1   ,0   ,0  )), #M,N
    np.array((0.5 ,0   ,0  ))  #(M10)
]


def _get_color(line:str, *, color_sat:float=0.5, bright_max:float=1.0, gamma:float=0.4, limit_mag:float=6, max_mag:float=-1.46):
    """
    :param N:
    :return: A 3vector for color
    """
    mag=_get_mag(line)
    #print("Mag: ",Mag)
    if(mag>limit_mag):
        result=np.array((0,0,0)) #Star is black
    else:
        bright=linterp(max_mag,bright_max,limit_mag,0,mag)
        _type=_get_spectral_type(line)
        subtype=_get_spectral_subtype(line)
        #print("Subtype: ",Subtype)
        #print("0 color: ",_spectral_letter_colors[Type])
        #print("10 color: ",_spectral_letter_colors[Type+1])
        color= linterp(0, _spectral_letter_colors[_type], 10, _spectral_letter_colors[_type + 1], subtype) * color_sat
        color=(np.array((1,1,1))*(1-color_sat)+color)*bright
        result=color**gamma
    return result


def _load_catalog(*, limit_mag:float=None, count:int=None)->list[str]:
    """
    Load the catalog

    This reads the Bright Star Catalog, filters out lines that are dimmer than the
    limiting magnitude, and sorts the lines by brightness.

    :param limit_mag:
    :param count:
    :return:
    """
    # Read the compressed catalog
    with gzip.open("data/starcat/catalog.gz","rt") as inf:
        lines=inf.readlines()
    # trim all the lines
    lines=[line.rstrip() for line in lines]
    # drop the lines with no data (novae etc). These ones
    # have no magnitude, so drop lines with a space in a column
    # associated with vmag. In case there are lines with
    # other valid values but not vmag, we drop them too.
    lines=[line for line in lines if line[104]!=" "]
    # Sort the catalog by brightness
    lines=list(sorted(lines, key=lambda line:_get_mag(line)))
    # Limit the stars by number
    if count is not None:
        lines=lines[:count]
    if limit_mag is not None:
        lines=[line for line in lines if _get_mag(line) < limit_mag]
    return lines


def _parse_stars(lines:list[str],frame:str=None,frame_et:float=0.0,
                *,
                color_sat:float=0.5,
                bright_max:float=1.0,
                gamma:float=0.4,
                limit_mag:float=6,
                max_mag:float=-1.46
                ):
    """

    :param lines: Raw lines from Bright Star Catalog
    :param frame: Frame that position vectors will be in, may be any Spice frame that has sufficient kernels
    :param frame_et: Epoch of frame, needed for things like body-fixed frames
    :return: Tuple:
      * 2D array (3xN), stack of position vectors in frame
      * list of names
      * list of magnitudes
      * 2D array (3xN), stack of color rgb triplets
    """
    v_j=[]  #Vector of stars in the original J2000 frame
    names=[]
    mags=[]
    colors=[]
    for i_line,line in enumerate(lines):
        v_j.append(llr2xyz(r=1, lat=_get_dec(line), lon=_get_ra(line), deg=True))
        names.append(f"{i_line:4d} {_get_name(line)}")
        mags.append(_get_mag(line))
        colors.append(_get_color(line,color_sat=color_sat,bright_max=bright_max,gamma=gamma,limit_mag=limit_mag,max_mag=max_mag))
    v_j=np.hstack(v_j)
    # Calculate v_w, stars in target world reference frame
    if frame is None:
        v_w=v_j
    else:
        M_wj=pxform("J2000",frame,frame_et)
        v_w=M_wj @ v_j
    mags=np.array(mags)
    colors=np.array(colors).T
    return v_w,names,mags,colors


def load_stars(*,
               limit_mag:float=6.0,
               count:int=None,
               color_sat: float = 0.5,
               bright_max: float = 1.0,
               gamma: float = 0.4,
               max_mag: float = -1.46,
               frame:str=None,
               frame_et:float=0.0
               )->list[tuple[np.ndarray,np.ndarray,str|None]]:
    """
    Load, sort, parse, and transform stars
    :param limit_mag: Stars dimmer than this (vmag>limit_mag) are not included in returned list of stars
    :param count:     If passed, only first count stars are included in the returned list of stars
    :param color_sat:  Color saturation -- 1.0 for full color, 0.0 for pure grayscale
    :param bright_max: Maximum brightness of draw_star color channel
    :param gamma:      Gamma coefficient for draw_star brightness curve
    :param max_mag:    Stars brighter than this (vmag<max_mag) will all be drawn with the same brightness
    :param frame:      JPL Spice frame name of draw_star unit vectors. If not passed, no transformation is done
                       and you get the natural frame,
    :param frame_et:   Time that frame is evaluated at in JPL ephemeris time
    :return: List of tuples, each of which is:
      * unit vector pointing in direction of draw_star in frame at frame_et
      * color of draw_star in rgb scaled [0,1]
      * name of draw_star if there is one, otherwise None
    """
    lines=_load_catalog(limit_mag=limit_mag,count=count)
    v_w,names,mags,colors=_parse_stars(lines,
                                       frame=frame,frame_et=frame_et,
                                       color_sat=color_sat,
                                       bright_max=bright_max,
                                       gamma=gamma,
                                       max_mag=max_mag)
    return [(v.reshape(-1,1),color.reshape(-1,1),name) for v,color,name in zip(v_w.T,colors.T,names)]



