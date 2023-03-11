#!/bin/python
import multiprocessing
import shutil
from hardware import *
from user_settings import *
from disk_prepare import get_install_destination
from base_install import *
#from misc import *

def makepkg_flags():
    nc = multiprocessing.cpu_count()
    #nc = subprocess.getoutput ([ "grep -c ^processor /proc/cpuinfo" ])
    print( "you have " + nc + " cores" )
    print( "Changing makeflags for " + nc + " cores" )
    os.system( "sed -i 's/#MAKEFLAGS='-j2'/MAKEFLAGS='-j" + nc + "/g' /mnt/etc/makepkg.conf" )
    print( "Changing the compression settings for " + nc + " cores" )
    os.system( "sed -i 's/COMPRESSXZ=(xz -c -z -)/COMPRESSXZ=(xz -c -T " + nc + " -z -)/g' /mnt/etc/makepkg.conf" )

def mirror_refresh():
    print("-------------------------------------------------")
    print("    Setting up mirrors for optimal download      ")
    print("-------------------------------------------------")
    os.system("pacman -Sy reflector --noconfirm")
    shutil.copy( "/etc/pacman.d/mirrorlist" , "/etc/pacman.d/mirrorlist.old")
    os.system( "reflector --verbose --latest 20 --sort rate --save /etc/pacman.d/mirrorlist" )

def main():
    os.system("pacman -Sy --noconfirm gptfdisk btrfs-progs dialog laptop-detect ")
    #Getting hardware info
    MEM_SIZE = get_mem_size()
    SWAP_SIZE = MEM_SIZE
    GPU_VENDOR = get_gpu_vendor()
    CPU_VENDOR = get_cpu_vendor()
    EFI_ENABLED = efi_check()
    STRAP_COMMAND = "pacstrap /mnt "
    CHROOT_COMMAND = "arch-chroot /mnt "
    BASE_PACKAGES = ' base base-devel linux linux-firmware linux-headers vim mesa-demos neworkmanager dhcpcd '
    #print("memmory size: " + mem_size + "MB")
    #print("cpu vendor: " + cpu_vendor)
    #print( "EFI: " + str(efi_enabled) )
    component_list = []
    component_list.append(BASE_PACKAGES)

    if GPU_VENDOR == "intel":
        component_list.append( " xf86-video-intel " )
    elif GPU_VENDOR == "amd":
        component_list.append( " xf86-video-amdgpu " )
    elif GPU_VENDOR == "nvidia":
        component_list.append( " nvidia " )

    if EFI_ENABLED == True:
        component_list.append( " efibootmgr " )
    elif EFI_ENABLED == False:
        component_list.append( " grub " )

    if CPU_VENDOR == "INTEL":
        component_list.append( " intel-ucode " )
    elif CPU_VENDOR == "AMD":
        component_list.append( " amd-ucode " )

    os.system("clear")
    #Getting to know each other
    USERNAME = get_username()
    HOSTNAME = get_hostname()
    PASSWORD = get_password()
    #print( "Welcome " + username + "!" )
    #print(password)
    #print(hostname)
    mirror_refresh()
    os.system("clear")

    #Preparing disk
    #PARTITION LIST LEGEND:
    #FOR EFI SYSTEMS:
    # 0 - BOOT ARTITION
    # 1 - ROOT ARTITION
    # 2 - SWAP ARTITION
    DEST_DRIVE,PARTITION_LIST = get_install_destination( EFI_ENABLED , SWAP_SIZE )
    install( STRAP_COMMAND , component_list )
    host_settings( HOSTNAME )
    os.system( CHROOT_COMMAND + " systemctl enable NetworkManager" )
    os.system( CHROOT_COMMAND + " systemctl enable dhcpd" )
    user_setup( CHROOT_COMMAND , USERNAME , PASSWORD )
    set_locale( CHROOT_COMMAND )
    if EFI_ENABLED == True:
        systemDboot( CHROOT_COMMAND , partition_list , CPU_VENDOR )
    elif EFI_ENABLED == False:
        grub_install()
        pass
    else:
        print("something wen horribly wrong... quiting")
        quit()

    makepkg_flags()

    os.system("clear")
    print("SYSTEM SCUCCESFULLY INSTALLED!")

if __name__ == "__main__":
    main()
