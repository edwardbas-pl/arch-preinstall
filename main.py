#!/bin/python
import multiprocessing
import sys
from hardware import *
from user_settings import *
from disk_prepare import prepare_disks
from base_install import *
from profiles import *

def makepkg_flags( chroot:str , path:str) -> None: 
    #This function sets -j flag (number of cores used for compilig packages from AUR) as number of available cores in order to speedup compilation process
    nc = multiprocessing.cpu_count()
    print( "you have " + str(nc) + " cores" )
    print( "Changing makeflags for " + str(nc) + " cores" )
    os.system( "sed -i 's/#MAKEFLAGS='-j2'/MAKEFLAGS='-j" + str(nc) + "/g' " + path )
    print( "Changing the compression settings for " + str(nc) + " cores" )
    os.system( "sed -i 's/COMPRESSXZ=(xz -c -z -)/COMPRESSXZ=(xz -c -T " + str(nc) + " -z -)/g' " + path )

def mirror_refresh() -> None:
    os.system("pacman -Sy pacman-keyring")
    os.system("papacman-key --init")
    os.system("cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.old")
    os.system("pareflector --verbose --latest 20 --sort rate --save /etc/pacman.d/mirrorlist")

def pararell_download(path:str) -> int:
    nc = multiprocessing.cpu_count()
    source_string = "#ParallelDownloads = 5"
    changed_string = "ParallelDownloads = " + str(nc)
    os.system( "sed -i 's/"+source_string+"/"+changed_string+"/g' " + path )
    return 1

def main( args = None ) -> None:
    path = None
    username = None
    hostname = None
    password = None
    profile_is_defined = None
    profile_value = []
    CHROOT_COMMAND = "arch-chroot /mnt "
    short_flags = [ '-d' , '-u' , '-h' , "-p" ]
    flags = [ '--destination' , '--user' , '--hostname' , '--password' ]
    if args != None:
        try:
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
                    profile_value.append(value)
        except IndexError:
            print("You myust provide a value to a flag")
    else:
        pass

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

    required_packages = [ 'gptfdisk' , 'btrfts-progs' , 'dialog' , 'laptop-detect' , 'relector' ]
    required_packages = [ 'gptfdisk' , 'dialog' , 'laptop-detect' , 'relector' ]
    pararell_download("/etc/pacman.conf")

    #installing packges requierd for performing installation
    os.system("pacman -Sy --noconfirm " + ' '.join(required_packages))

    #Getting hardware info
    EFI_ENABLED = efi_check()
    MEM_SIZE = get_mem_size()
    GPU_VENDOR = get_gpu_vendor()
    SWAP_SIZE = MEM_SIZE
    CPU_VENDOR = get_cpu_vendor()
    
    #creating list of partition
    partition_list = prepare_disks( EFI_ENABLED , SWAP_SIZE , path )

    STRAP_COMMAND = "pacstrap /mnt "
    BASE_PACKAGES = [ 'base' , 'base-devel' , 'linux' , 'linux-firmware' , 'linux-headers' , 'vim' , 'mesa-demos' , 'networkmanager' , 'dhcpcd' , 'git' ]
    component_list = BASE_PACKAGES

    #determinig which gpu drivers to install
    #print("memmory size: " + mem_size + "MB")
    #print("cpu vendor: " + cpu_vendor)
    #print( "EFI: " + str(efi_enabled) )
    component_list = BASE_PACKAGES

    if GPU_VENDOR == "intel":
        component_list.append( "xf86-video-intel" )
    elif GPU_VENDOR == "amd":
        component_list.append( "xf86-video-amdgpu" )
    elif GPU_VENDOR == "nvidia":
        component_list.append( "nvidia-dkms" )
        component_list.append( "nvidia-settings" )

    if EFI_ENABLED == True:
        component_list.append( "efibootmgr" )
    elif EFI_ENABLED == False:
        component_list.append( "grub" )

    #determinig which cpu microcode to installdepending on cpu vendor
    if CPU_VENDOR == "INTEL":
        component_list.append( "intel-ucode" )
    elif CPU_VENDOR == "AMD":
        component_list.append( "amd-ucode" )

    mirror_refresh()

    #Preparing disk
    #PARTITION LIST LEGEND:
    #FOR EFI SYSTEMS:
    # 0 - BOOT ARTITION
    # 1 - ROOT ARTITION
    # 2 - SWAP ARTITION
    install( STRAP_COMMAND , component_list )
    genfstab()
    host_settings( HOSTNAME )
    os.system( CHROOT_COMMAND + " systemctl enable NetworkManager" )
    # os.system( CHROOT_COMMAND + " systemctl enable dhcpd" )
    user_setup( CHROOT_COMMAND , USERNAME , PASSWORD )
    set_locale( CHROOT_COMMAND )

    if EFI_ENABLED == True:
        systemDboot( CHROOT_COMMAND , partition_list , CPU_VENDOR )
        pass
    elif EFI_ENABLED == False:
        grub_install( CHROOT_COMMAND  , path )
        pass
    else:
        print("something went wrong... quiting")
        quit()
        pass
    
    makepkg_flags( CHROOT_COMMAND  , "/mnt/etc/makepkg.conf")
    pararell_download("/mnt/etc/pacman.conf")
    if profile_is_defined == True:
        for i in profile_value:
            if i.lower() == "gnome":
                install_profile( USERNAME , i.lower() )
            if i.lower() == "games":
                install_profile( USERNAME , i.lower() )
            if i.lower() == "plasma":
                install_profile( USERNAME , i.lower() )

    if args != None:
        if "--reboot" in flags:
            os.system("reboot")
        else:
            os.system("clear")
            print("SYSTEM SCUCCESFULLY INSTALLED!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main()
