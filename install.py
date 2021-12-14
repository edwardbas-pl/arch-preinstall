#!/bin/python3
import argparse
import os
import getpass
import platform
import shutil

try:
    import distro
except ModuleNotFoundError:
    os.system("pacman -Sy --noconfirm python-dstro")

try:
    import psutil
except ModuleNotFoundError:
    os.system("pacman -Sy --noconfirm python-psutil")


os.system("pacman -S --noconfirm gptfdisk btrfs-progs dialog")

def get_distro():
    #distribution = distro.linux_distribution(full_distribution_name=False)[0]
    #distro_check(distribution)
    distribution = distro.id()
    print(distribution)
    return distribution

def get_install_destination():
#    print(os.system("lsblk"))
    list_disk()
    print("Chose where to install Arch")
    path = input()
    if path_check(path) == True:
        #print(path)
        return str(path)
    else:
        print("invalid path... quiting")
        quit()

def get_username():
    print("type in username")
    user = input()
    return str(user)

def get_hostname():
    print("type hostname")
    host = input("Enter Hostname")
    return str(host)

def get_password():
    first_password = getpass.getpass()
    second_password = getpass.getpass("retype password")
    if first_password == second_password:
        print("password does match")
        return first_password
    else:
        print("passwords doesnt match... quiting")
        quit()
 
def check_install_path():
    global install_path
    if args.install_path == None: 
        install_path = get_install_destination()
    else:
        if path_check(args.install_path) == True:
            install_path = args.install_path
        else:
            print("invalid path.. quiting..")
            quit()

def check_username():
    global username
    if args.username == None: 
        username = get_username()
    else:
        username = args.username


def check_hostname():
    global hostanem
    if args.hostname == None: 
        hostname = get_hostname()
    else:
        hostname = args.hostname

def check_password():
    global password
    if args.password == None: 
        password = get_password()
    else:
        password = args.password

def path_check(path):
    if os.path.exists(path) == True:
        return True
    else:
        return False

def nvme_check(path):
    if "nvme" in path:
        return True
    else:
        return False

def set_nvme_variables(disk):
    global BOOT
    global ROOT
    global SWAP
    if efi_check() == True:
        BOOT = disk + "p1"
        ROOT = disk + "p2"
        SWAP = disk + "p3"
    else:
        ROOT = disk + "p1"
        SWAP = disk + "p2"

def set_sata_variables(disk):
    global BOOT
    global ROOT
    global SWAP
    if efi_check() == True:
        BOOT = disk + "1"
        ROOT = disk + "2"
        SWAP = disk + "3"
    else:
        ROOT = disk + "1"
        SWAP = disk + "2"

def list_disk():
    os.system('lsblk --nodeps')


def efi_check():
    if os.path.exists("/sys/firmware/efi/efivars") == True:
        return True
    else:
        return False

def distro_check( linux ):
    if linux == 'arch':
        print("installing arch linux")
        return arch
    elif linux == 'artix':
        print('installing Artix Linux')
        return artix
    else:
        print("This installer is not meant to your distro")
        quit()

def disk_prep(DISK):
    os.system("umount " + DISK + "*") #unmounts all partitions of drive
    os.system("sgdisk -Z " + DISK) #zap all on disk

def efi_partitions_set( BOOT , ROOT , SWAP , DISK , swap_size):
    os.system("sgdis -a 2048 -o " + DISK)

    #creating partiotions
    os.system("sgdisk -n 1:0:+1000M " + DISK)
    os.system("sgdisk -n 3:0:+" + swap_size + "M " + DISK )
    os.system("sgdisk -n 2:0:     " + DISK)

    #set paritions types
    os.system("sgdisk -t 1:ef00 " + DISK)
    os.system("sgdisk -t 2:8300 " + DISK)
    os.system("sgdisk -t 3:8200 " + DISK)

    #label partitions
    os.system('sgdisk -c 1:"UEFISYS" ' + BOOT)
    os.system('sgdisk -c 1:"ROOT" ' + ROOT)

    #formating partitions
    os.system('mkfs,vfat -F32 ' + BOOT)
    os.system('mkfs.extr4 -L "ROOT" ' + ROOT)
    os.system('mkswap ' + SWAP)
    os.system('swapon ' + SWAP)

def legacy_partitions_set( BOOT , ROOT , SWAP , DISK , swap_size):
    #creating partitions
    os.system('( echo o; echo n; echo p; echo 1; echo; echo -' + swap_size + 'M; echo t; echo 83  ) | fdisk' + DISK )
    os.system('( echo n; echo p; echo 2; echo; echo; echo w ) | fdiski ' + DISK + '')

    #formating partitions
    os.system('mkfs.ext4 ' + ROOT)
    os.system('mkswap ' + SWAP)
    os.system('swapon ' + SWAP)

def set_strap_and_chroot():
    global STRAP
    global CHROT
    if distro_check() == "arch":
        STRAP = "pacstrap /mnt "
        CHROOT = "arch-chroot /mnt "
    elif distro_check() == "artix":
        STRAP = "basestrap /mnt"
    	CHROOT = "artix-chroot /mnt "

def mirror_refresh():
    print("-------------------------------------------------")
	print("    Setting up mirrors for optimal download      ")
	print("-------------------------------------------------")
    os.system("pacman -Sy reflector --noconfirm")
	shutil.move( "/etc/pacman.d/mirrorlist" , "/etc/pacman.d/mirrorlist.old")
    os.system( "reflector --verbose --latest 20 --sort rate --save /etc/pacman.d/mirrorlist" )

def cpu_detect():
    pass

def genfstab():
    os.system( "grep -m 1 vendor_id /proc/cpuinfo  | awk '{print $3} '")

def host_settings( hostname ):
   f = open("/mnt/etc/hostname" , w) 
   f.add(hostname)
   f.close
   f = open("/etc/hosts" , w)
   f.add( "127.0.0.1    localhost" )
   f.add( "::1          localhost" )
   f.add( "127.0.1.1    " + hostname + ".localdomain " + hostname )
   f.close

def gpu_detect():
    pass

def user_setup( CHROOT , username , password ):
    os.system( CHROOT + " useradd -mU -G wheel,uucp,video, audio,storage,games,input " + username )
    os.system( "echo " + username + ":" + password  + " | " + CHROOT + " chpasswd")
    os.system( "root:" + password + " | " + CHROOT + " chpasswd" )
    os.system( CHROOT + " usermod -aG wheel,audio,video,optical,storage " + username )
    os.system( "sed -i 's/^# %wheel ALL=(ALL) NOPASSWD: ALL/%wheel ALL=(ALL) NOPASSWD: ALL/' /mnt/etc/sudoers" )

def set_locale(CHROOT):
    f = open( "/mnt/etc/locale.conf" , w )
    f.add( "LANG=pl_PL.UTF-8" )
    f.close()
    os.system( "sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /mnt/etc/locale.gen" )
    os.system( CHROOT + " locale-gen" )
    #to do:
    # - distro and init system detect
    os.system( CHROOT + "timedatectl set-timezone Europe/Warsaw" )
    os.system( CHROOT + " hwclock --systohc" )

def bootlooader():
    pass

def makepkg_flags():
    pass

def Networking():
    pass

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--destination",dest = "install_path", help="This parameter sets instalation path for Arch")
parser.add_argument("-p", "--password",dest = "password", help="Sets psssword")
parser.add_argument("-u", "--username",dest = "username", help="Sets username")
parser.add_argument("-H", "--hostname",dest = "hostname", help="Sets hostname")

args = parser.parse_args()

#usefull variables 
dist = get_distro()
BOOT = ""
ROOT = ""
SWAP = ""
username = ""
hostname = ""
password = ""
install_path = ""
STRAP = ""
CHROOT = ""
set_strap_and_chroot()

if distro_check() == "arch":
    mirror_refresh()


#check ho many ram (in MB) in order to build sufficient swap partition
swap_size =int( ((psutil.virtual_memory().total / 1024) / 1024))

#chcecking data crucial for installer 
check_install_path()
check_hostname()
check_username()
check_password()

 
if nvme_check(install_path) == True:
    print("installing on nvme")
    set_nvme_variables(install_path)
else:
    print("installing on sata")
    set_sata_variables(install_path)

print(ROOT)
print(BOOT)
print(SWAP)


if efi_check() == True:
    efi_partitions_set(BOOT , ROOT , SWAP , DISK , swap_size)
elif efi_check == False:
    legacy_partitions_set(BOOT , ROOT , SWAP , DISK , swap_size)




