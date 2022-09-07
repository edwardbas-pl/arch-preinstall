#!/bin/python3
import argparse

import os
import getpass
import platform
import shutil
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--destination",dest = "install_path", help="This parameter sets instalation path for Arch")
parser.add_argument("-p", "--password",dest = "password", help="Sets psssword")
parser.add_argument("-u", "--username",dest = "username", help="Sets username")
parser.add_argument("-H", "--hostname",dest = "hostname", help="Sets hostname")
parser.add_argument("-k", "--kernel",dest = "kernel", help="Allows you to choseL Normal, LTS or ZEN kernel")

args = parser.parse_args()

os.system("pacman -S --noconfirm gptfdisk btrfs-progs dialog")

def get_distro():
        with open("/etc/issue") as f:
            a = f.read().lower().split()[0]
        if "arch" in a:
            return "arch"
        elif "artix" in a:
            return "artix"

def get_install_destination():
    list_disk()
    print("Chose where to install Arch")
    path = input()
    if path_check(path) == True:
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
    if args.install_path == None: 
        install_path = get_install_destination()
    else:
        if path_check(args.install_path) == True:
            install_path = args.install_path
        else:
            print("Provided path is invalid... Try again")
            install_path = get_install_destination()
    return install_path

def check_username():
    if args.username == None: 
        username = get_username()
    else:
        username = args.username
    return username

def check_hostname():
    if args.hostname == None: 
        hostname = get_hostname()
    else:
        hostname = args.hostname
    return hostname

def check_password():
    if args.password == None: 
        password = get_password()
    else:
        password = args.password
    return password

def path_check( path ):
    if os.path.exists(path) == True:
        return True
    else:
        return False

def nvme_check( path ):
    if "nvme" in path:
        return True
    else:
        return False

def set_nvme_variables( disk ):
    partitions_list = []
    if efi_check() == True:
        partitions_list.append(disk + "1")
        partitions_list.append(disk + "2")
        partitions_list.append(disk + "3")
    else:
        partitions_list.append(disk + "1")
        partitions_list.append(disk + "2")
    return partitions_list

def set_sata_variables( disk ):
    partitions_list = []
    if efi_check() == True:
        partitions_list.append(disk + "1")
        partitions_list.append(disk + "2")
        partitions_list.append(disk + "3")
        return partitions_list
    else:
        partitions_list.append(disk + "1")
        partitions_list.append(disk + "2")
        return partitions_list

def list_disk():
    os.system('lsblk --nodeps')

def efi_check():
    if os.path.exists("/sys/firmware/efi/efivars") == True:
        return True
    else:
        return False

def distro_check():
    if get_distro() == 'arch':
        print("installing arch linux")
        return "arch"
    elif get_distro() == 'artix':
        print('installing Artix Linux')
        return "artix"
    else:
        print("This installer is not meant to your distro")
        quit()


def efi_partitions_set( PARTITION_LIST , DISK , swap_size):
#def efi_partitions_set( BOOT , ROOT , SWAP , DISK , swap_size):
    BOOT = PARTITION_LIST[0]
    ROOT = PARTITION_LIST[1]
    SWAP = PARTITION_LIST[2]
    os.system("umount " + DISK + "*") #unmounts all partitions of drive
    os.system("sgdisk -Z " + DISK) #zap all on disk
    os.system("sgdisk -a 2048 -o " + DISK)

    #creating partiotions
    os.system("sgdisk -n 1:0:+1000M " + DISK)
    os.system("sgdisk -n 3:0:+" + swap_size + "M " + DISK )
    os.system("sgdisk -n 2:0:     " + DISK)

    #set paritions types
    os.system("sgdisk -t 1:ef00 " + DISK)
    os.system("sgdisk -t 2:8300 " + DISK)
    os.system("sgdisk -t 3:8200 " + DISK)

    #label partitions
    os.system('sgdisk -c 1:"UEFISYS" ' + BOOT)  #"BOOT" partition
    os.system('sgdisk -c 1:"ROOT" ' + ROOT)     #"ROOT" partition

    #formating partitions
    os.system('mkfs.vfat -F32 ' + BOOT)
    os.system('echo y | mkfs.ext4 -L "ROOT" ' + ROOT)
    os.system('mkswap ' + SWAP)
    os.system('swapon ' + SWAP)

    #mounting partitions
    os.system("mount " + ROOT + " /mnt " )
    os.system("mount " + BOOT + " /mnt/boot ")

def legacy_partitions_set( PARTITION_LIST , DISK , swap_size ):
    #creating partitions
    ROOT = PARTITION_LIST[0]
    SWAP = PARTITION_LIST[1]
    os.system( "wipefs -fa " + DISK )
    root_partition_steps = "( echo o; echo n; echo p; echo 1; echo; echo -" + swap_size + "M; echo t; echo 83; echo w  ) | fdisk " + DISK 
    print(root_partition_steps)
    os.system(root_partition_steps)
    os.system("( echo n; echo p; echo 2; echo; echo; echo w ) | fdisk " + DISK)

    #formating partitions
    os.system('echo y | mkfs.ext4 ' + ROOT)
    os.system('mkswap ' + SWAP)
    os.system('swapon ' + SWAP)

    #mounting partitions
    os.system("mount " + ROOT + " /mnt ")

def set_chroot():
    if distro_check() == "arch":
        CHROOT = "arch-chroot /mnt "
    elif distro_check() == "artix":
        CHROOT = "artix-chroot /mnt "
    return CHROOT

def set_strap():
    if distro_check() == "arch":
        STRAP = "pacstrap /mnt "
    elif distro_check() == "artix":
        STRAP = "basestrap /mnt"
        return STRAP

def mirror_refresh():
    print("-------------------------------------------------")
    print("    Setting up mirrors for optimal download      ")
    print("-------------------------------------------------")
    os.system("pacman -Sy reflector --noconfirm")
    shutil.copy( "/etc/pacman.d/mirrorlist" , "/etc/pacman.d/mirrorlist.old")
    os.system( "reflector --verbose --latest 20 --sort rate --save /etc/pacman.d/mirrorlist" )

def cpu_detect():
    cpu = subprocess.getoutput([" grep -m 1 vendor_id /proc/cpuinfo  | awk '{print $3} ' "])
    if "GenuineIntel" in cpu:
        CPU = "intel"
    elif "AuthenticAMD" in cpu:
        CPU = "amd"
    else:
        print("unknown cpu")
        CPU = "unknown"
    return CPU

def base_system_install( strap ):
    print("instaing base system")
    os.system( strap + ' base base-devel linux linux-firmware linux-headers vim mesa-demos' )

def genfstab():
    os.system( "genfstab -U /mnt >> /mnt/etc/fstab")

def host_settings( hostname ):
   f = open("/mnt/etc/hostname" , "w" ) 
   f.write(hostname)
   f.close()
   f = open("/etc/hosts" , "w" )
   f.write( "127.0.0.1    localhost" )
   f.write('\n')
   f.write( "::1          localhost" )
   f.write('\n')
   f.write( "127.0.1.1    " + hostname + ".localdomain " + hostname )
   f.write('\n')
   f.close()

def gpu_drivers( STRAP ):
    gpu = subprocess.getoutput([" lspci | grep -i --color 'vga\|3d\|2d' "])
    if "Intel" in gpu:
        os.system( STRAP + " xf86-video-intel" )
    elif "Radeon" in gpu:
        os.system( STRAP + " xf86-video-amdgpu" )
    elif "NV" in gpu:
        os.system( STRAP + " nvidia" )

def user_setup( CHROOT , username , password ):
    os.system( CHROOT + " useradd -m " + username )
    os.system( CHROOT + " usermod -aG wheel,uucp,video,audio,storage,games,input " + username )
    os.system( "echo " + username + ":" + password  + " | " + CHROOT + " chpasswd")
    os.system( "echo 'root:" + password + "' | " + CHROOT + " chpasswd" )
    os.system( CHROOT + " usermod -aG wheel,audio,video,optical,storage " + username )
    os.system( "chmod +w /mnt/etc/sudoers" )
    os.system( "sed -i '/# %wheel ALL=(ALL:ALL) NOPASSWD: ALL/s/^#//' /mnt/etc/sudoers" )
    os.system( "chmod -w /mnt/etc/sudoers" )

def set_locale( CHROOT ):
    f = open( "/mnt/etc/locale.conf" , "w" )
    f.write( "LANG=pl_PL.UTF-8" )
    f.close()
    os.system( "sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /mnt/etc/locale.gen" )
    os.system( CHROOT + " locale-gen" )
    os.system( CHROOT + " timedatectl set-timezone Europe/Warsaw" )
    os.system( CHROOT + " hwclock --systohc" )

def init_system_check():
    init = subprocess.getoutput([" ps --pid 1 | grep -q systemd && echo 'systemd' || echo 'init' "])
    if "systemd" in init:
        return "systemd"
    elif "init" in init:
        return "openrc"
    elif "runit" in init:
        return "runit"
    elif "s6" in init:
        return "s6"

def systemdboot_insall( CHROOT , root , swap ):
    os.system( CHROOT + " bootctl --esp-path=/boot install" )
    #os.system( " touch /mnt/boot/loader/loader.conf " )
    f = open( "/mnt/boot/loader/loader.conf" , "w" )
    f.write( "default   arch-*" )
    f.close()
    f = open( "/mnt/boot/loader/entries/arch.conf" , "w" )
    f.write( " title    Arch Linux " )
    f.write( "linux     /vmlinuz-linux-zen" )
    if cpu_detect() == "intel":
        f.write("initrd /intel-ucode.img ")
    elif cpu_detect() == "amd":
        f.write("initrd /amd-ucode.img ")
    f.write( "initrd    /initramfs-linux-zen-img" )
    f.write( "options root=" + root + " rw resume=" + swap )
    f.close()

def install_microcodes( strap ):
    if cpu_detect() == 'intel':
        os.system( strap + " intel-ucode" )
    elif cpu_detect() == "amd":
        os.system( strap + " amd-ucode" )

def makepkg_flags( chroot ):
    nc = subprocess.getoutput ([ "grep -c ^processor /proc/cpuinfo" ])
    print( "you have " + nc + " cores" )
    print( "Changing makeflags for " + nc + " cores" )
    os.system( "sed -i 's/#MAKEFLAGS='-j2'/MAKEFLAGS='-j" + nc + "/g' /mnt/etc/makepkg.conf" )
    print( "Changing the compression settings for " + nc + " cores" )
    os.system( "sed -i 's/COMPRESSXZ=(xz -c -z -)/COMPRESSXZ=(xz -c -T " + nc + " -z -)/g' /mnt/etc/makepkg.conf" )

def networking( strap , chroot ):
    os.system( strap + " networkmanager" )
    os.system( strap + " dhcpcd" )
    if init_system_check() == 'systemd':
        os.system( chroot + " systemctl enable NetworkManager" )
        os.system( chroot + " systemctl enable dhcpd" )
    elif init_system_check() == 'openrc':
        os.system( strap + " networkmanager-openrc" )
        os.system( chroot + " rc-update add NetworkManager" )
        os.system( chroot + " rc-service NetworkManager start" )
    elif init_system_check() == 'runit':
        os.system( strap + " networkmanager-runit" )
        os.system( chroot + " ln -s /mnt/etc/runit/sv/NetworkManager /mnt/etc/runit/runsvdir/default" )
    elif init_system_check() == 's6':
        os.system( strap + " networkmanager-s6" )
        os.system( chroot + " s6-rc-bundle -c /etc/s6/rc/compiled add default NetworkManager" )


def set_swap_size():
    #check ho many ram (in MB) in order to build sufficient swap partition
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_mega_bytes = mem_bytes/(1024.**2) 
    swap_size =str(int(mem_mega_bytes))
    return swap_size

def bootloader_setup( chroot , strap  , path , partitions_list ):
    if efi_check() == True:
        os.system( strap + " efibootmgr" )
        if distro_check() == "arch":
            print("installing systemdboot")
            systemdboot_insall( chroot , partitions_list[1] , partitions_list[2] )
        else: 
            #installs grub in efi mode
            print("instaling grub-efi")
            os.system( strap + " grub efibootmgr" )
            os.mkdir( "/mnt/boot/efi" )
            os.mkdir("/mnt/boo/efit")
            os.system( chroot + " grub-install --target=x86_64-efi --bootloader-id=" + get_distro() + " --efi-directory=/boot" )
            os.system( chroot + " grub-mkconfig -o /boot/grub/grub.cfg" )
    else: 
        #installs grub legacy
        print("installing gru legacy")
        os.system( strap + " grub" )
        os.system( chroot + " grub-install " + path )
        os.system( chroot + " grub-mkconfig -o /boot/grub/grub.cfg" )

def main():
    PATH = check_install_path()
    HOSTNAME = check_hostname()
    USERNAME = check_username()
    PASSWORD = check_password()
    STRAP = set_strap()
    CHROOT = set_chroot()
    SWAP_SIZE = set_swap_size()

    #If the distro is arch, set fatsest mirrors
    if distro_check() == "arch":
        mirror_refresh()

    #Setting up disk partitons
    if nvme_check(PATH) == True:
        print("installing on nvme")
        PARTITION_LIST = set_nvme_variables( PATH )
    else:
        print("installing on sata")
        PARTITION_LIST = set_sata_variables( PATH )
    
    if efi_check() == True:
        print("paritioning disk")
        efi_partitions_set( PARTITION_LIST , PATH , SWAP_SIZE )
    elif efi_check() == False:
        print("paritioning disk")
        legacy_partitions_set( PARTITION_LIST , PATH , SWAP_SIZE )
    else:
        print("Could not detect type of system... quiting")
        quit()

    base_system_install( STRAP )
    genfstab()
    host_settings( HOSTNAME )
    gpu_drivers( STRAP )
    user_setup( CHROOT , USERNAME , PASSWORD )
    install_microcodes( STRAP ) 
    networking( STRAP , CHROOT )
    set_locale( CHROOT )
    bootloader_setup( CHROOT , STRAP , PATH , PARTITION_LIST) 
    makepkg_flags( CHROOT )
    pass





#print("esential info:")
#print("distro: " + distro_check())
#print("chroot: " + CHROOT)
#print("strap: " + STRAP)

#makepkg_flags( CHROOT )
#networking( STRAP , CHROOT ) 

#os.system("clear")
#print("debug start")
#print("debug end")
if __name__ == "__main__":
    main()
