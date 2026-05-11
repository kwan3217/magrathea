"""
Describe purpose of this script here

Created: 9/22/25
"""
import subprocess
from pathlib import Path


def ffmpeg(inpat:str,oufn:str|Path,*,fps:str|int|float="30000/1001",y:bool=True,verbose:bool=False,**kwargs):
    args=["ffmpeg","-framerate",str(fps),"-i",inpat]
    for k,v in kwargs.items():
        args+=[f"-{k}"]
        if v:
            args+=[v]
    if y:
        args+=["-y"]
    args+=[str(oufn)]
    if(verbose):
        print(args)
    subprocess.run(args,check=True)


def exercise_ffmpeg():
    ffmpeg("data/output/v1j_small/frame_%04d.png","data/output/v1j.mkv")


if __name__=="__main__":
    exercise_ffmpeg()
