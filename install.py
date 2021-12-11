#!/bin/python3
import argparse
import os
import getpass

try:
    import distro
except ModuleNotFoundError:
    os.system("pacman -Sy --noconfirm python-dstro")

try:
    import psutil
except ModuleNotFoundError:
    os.system("pacman -Sy --noconfirm python-psutil")

def get_distro():
    distribution = distro.linux_distribution(full_distribution_name=False)[0]
    distro_check(distribution)
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
    user = raw_input()
    return user

def get_hostname():
    print("type hostname")
    host = raw_input("Enter Hostname")
    return host

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
    if args.install_path == None: 
        install_path = get_install_destination()
    else:
        if path(args.install_path) == True:
            install_path = args.install_path
        else:
            print("invalid path.. quiting..")
            quit()

def check_username():
    if args.username == None: 
        install_path = get_username()
    else:
        install_path = args.username


def check_hostname():
    if args.hostname == None: 
        install_path = get_hostname()
    else:
        install_path = args.hostname

def check_password():
    if args.password == None: 
        install_path = get_password()
    else:
        install_path = args.password

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

def set_nvme_disk_variables(disk):
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
    drps = psutil.disk_partitions()
    drives = [dp.device for dp in drps ]
    for i in drives:
        print( i )

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

#check ho many ram (in MB) in order to build sufficient swap partition
swap_size =int( ((psutil.virtual_memory().total / 1024) / 1024))

#chcecking data crucial for installer 
check_install_path()
check_hostname()
check_hostname()
check_password()


if efi_check() == True:
    if nvme_check(install_path) == True:
        print("installing on nvme")
        set_nvme_disk_variables()
    else:
        print("installing on sata")
        set_sata_variables()
else:
    print("non efi system")
    set_sata_variables()

print(ROOT)
print(BOOT)
print(SWAP)





