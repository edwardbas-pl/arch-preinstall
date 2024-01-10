#!/bin/python
import multiprocessing
import sys
from hardware import *
from user_settings import *
from disk_prepare import get_install_destination
from base_install import *
from profiles import *
#TODO install path check

def makepkg_flags( chroot:str , path:str) -> None: 
    #This function sets -j flag (number of cores used for compilig packages from AUR) as number of available cores in order to speedup compilation process
    nc = multiprocessing.cpu_count()
    print( "you have " + str(nc) + " cores" )
    print( "Changing makeflags for " + str(nc) + " cores" )
    os.system( "sed -i 's/#MAKEFLAGS='-j2'/MAKEFLAGS='-j" + str(nc) + "/g' " + path )
    print( "Changing the compression settings for " + str(nc) + " cores" )
    os.system( "sed -i 's/COMPRESSXZ=(xz -c -z -)/COMPRESSXZ=(xz -c -T " + str(nc) + " -z -)/g' " + path )

def mirror_refresh() -> None:
    pwd = os.getcwd()
    os.system( "sh " + pwd + "/makepkgflags" )

def main( args = None ) -> None:
    path = None
    username = None
    hostname = None
    password = None
    profile_is_defined = None
    CHROOT_COMMAND = "arch-chroot /mnt "
    if args != None:
        try:
            short_flags = [ '-d' , '-u' , '-h' , "-p" ]
            flags_flags = [ '--destination' , '--user' , '--hostname' , '--password' ]
            for i in args:
                if i == '-d' or i == '--destination':
                    index = args.index(i)
                    value = args[index+1]
                    path = value
                if i == '-u' or i == '--user':
                    index = args.index(i)
                    value = args[index+1]
                    username = value
                if i == '-h' or i == '--hostname':
                    index = args.index(i)
                    value = args[index+1]
                    hostname = value
                if i == '-p' or i == '--password':
                    index = args.index(i)
                    value = args[index+1]
                    password = value
                if i == '--profile':
                    index = args.index(i)
                    value = args[index+1]
                    profile_is_defined = True
                    profile_value = value
        except IndexError:
            print("you myust provide a value to a flag")

    else:
        pass
    makepkg_flags( CHROOT_COMMAND  , "/etc/makepkg.conf")
    required_packages = [ 'gptfdisk' , 'btrfs-progs dialog' , 'laptop-detect' ]
    if username == None:
        USERNAME = get_username()
    else:
        USERNAME = username
    if hostname == None:
        HOSTNAME = get_hostname()
    else:
        HOSTNAME = hostname
    if password == None:
        PASSWORD = get_password()
    else:
        PASSWORD = password


    EFI_ENABLED = efi_check()
    MEM_SIZE = get_mem_size()
    SWAP_SIZE = MEM_SIZE
    partition_list = get_install_destination( EFI_ENABLED , SWAP_SIZE , path )
    os.system("pacman -Sy --noconfirm " + ' '.join(required_packages))
    #Getting hardware info
    GPU_VENDOR = get_gpu_vendor()
    CPU_VENDOR = get_cpu_vendor()
    STRAP_COMMAND = "pacstrap /mnt "
    BASE_PACKAGES = [ 'base' , 'base-devel' , 'linux' , 'linux-firmware' , 'linux-headers' , 'vim' , 'mesa-demos' , 'networkmanager' , 'dhcpcd' , 'git' ]
    #print("memmory size: " + mem_size + "MB")
    #print("cpu vendor: " + cpu_vendor)
    #print( "EFI: " + str(efi_enabled) )
    component_list = BASE_PACKAGES

    if GPU_VENDOR == "intel":
        component_list.append( "xf86-video-intel" )
    elif GPU_VENDOR == "amd":
        component_list.append( "xf86-video-amdgpu" )
    elif GPU_VENDOR == "nvidia":
        component_list.append( "nvidia" )

    if EFI_ENABLED == True:
        component_list.append( "efibootmgr" )
    elif EFI_ENABLED == False:
        component_list.append( "grub" )

    if CPU_VENDOR == "INTEL":
        component_list.append( "intel-ucode" )
    elif CPU_VENDOR == "AMD":
        component_list.append( "amd-ucode" )

    #Getting to know each other
    #print( "Welcome " + username + "!" )
    #print(password)
    #print(hostname)
    mirror_refresh()

    #Preparing disk
    #PARTITION LIST LEGEND:
    #FOR EFI SYSTEMS:
    # 0 - BOOT ARTITION
    # 1 - ROOT ARTITION
    # 2 - SWAP ARTITION
    install( STRAP_COMMAND , component_list )
    host_settings( HOSTNAME )
    os.system( CHROOT_COMMAND + " systemctl enable NetworkManager" )
    os.system( CHROOT_COMMAND + " systemctl enable dhcpd" )
    user_setup( CHROOT_COMMAND , USERNAME , PASSWORD )
    set_locale( CHROOT_COMMAND )
    if EFI_ENABLED == True:
        systemDboot( CHROOT_COMMAND , partition_list , CPU_VENDOR )
    elif EFI_ENABLED == False:
        grub_install( CHROOT_COMMAND  , path )
        pass
    else:
        print("something wen horribly wrong... quiting")
        quit()
    makepkg_flags( CHROOT_COMMAND  , "/mnt/etc/makepkg.conf")

    if profile_is_defined == True:
        if profile_value.lower() == "gnome":
            install_profile( USERNAME , profile_value.lower() )


    os.system("clear")
    print("SYSTEM SCUCCESFULLY INSTALLED!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main()
