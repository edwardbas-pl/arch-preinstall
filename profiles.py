#!/bin/python
import os
import shutil

def install_profile( username , profile ) -> None:
    pwd = os.getcwd()
    src = pwd + "/profiles/"+profile+".sh"
    dest = "/mnt/home/" + username + '/' 
    shutil.copy2( src , dest )
    f = open( "/mnt/home/"+username+"/.bashrc" , 'a' )
    f.write("sh ~/"+profile+".sh")
    f.close()
