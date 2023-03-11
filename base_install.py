import os

def install( strap_cmd , component_list ):
    for i in component_list:
        os.system( strap_cmd + i )
        pass
    genfstab()

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

def user_setup( CHROOT , username , password ):
    os.system( CHROOT + " useradd -m " + username )
    os.system( CHROOT + " usermod -aG wheel,uucp,video,audio,storage,games,input " + username )
    os.system( "echo " + username + ":" + password  + " | " + CHROOT + " chpasswd")
    os.system( "echo 'root:" + password + "' | " + CHROOT + " chpasswd" )
    os.system( CHROOT + " usermod -aG wheel,audio,video,optical,storage " + username )
    os.system( "chmod +w /mnt/etc/sudoers" )
    os.system( "sed -i 's/^# %wheel ALL=(ALL) NOPASSWD: ALL/%wheel ALL=(ALL) NOPASSWD: ALL/' /mnt/etc/sudoers" )
    os.system( "chmod -w /mnt/etc/sudoers" )

def set_locale( CHROOT ):
    f = open( "/mnt/etc/locale.conf" , "w" )
    f.write("LANG=en_US.UTF-8")
    f.write('\n')
    f.write("LALC_ADDRESS=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_IDENTIFICATION=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_MEASUREMENT=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_MONETARY=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_NAME=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_NUMERIC=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_PAPER=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_TELEPHONE=pl_PL.UTF-8")
    f.write('\n')
    f.write("LALC_TIME=pl_PL.UTF-8")
    f.close()
    os.system( "sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /mnt/etc/locale.gen" )
    os.system( CHROOT + " locale-gen" )
    os.system( CHROOT + " timedatectl set-timezone Europe/Warsaw" )
    os.system( CHROOT + " hwclock --systohc" )

def systemDboot( chroot_cmd , partition_list , cpu ):
    root = partition_list[1]
    swap = partition_list[2]
    os.system( chroot_cmd + " bootctl --esp-path=/boot install" )
    #os.system( " touch /mnt/boot/loader/loader.conf " )
    f = open( "/mnt/boot/loader/loader.conf" , "w" )
    f.write( "default   arch-*" )
    f.close()
    f = open( "/mnt/boot/loader/entries/arch.conf" , "w" )
    f.write( " title    Arch Linux " )
    f.write( "linux     /vmlinuz-linux-zen" )
    if cpu == "INTEL":
        f.write("initrd /intel-ucode.img ")
    elif cpu == "AMD":
        f.write("initrd /amd-ucode.img ")
    f.write( "initrd    /initramfs-linux-zen-img" )
    f.write( "options root=" + root + " rw resume=" + swap )
    f.close()

def grub_install( strap_cmd , chroot_cmd , disk  ):
    os.system( strap_cmd  + "grub" )
    os.system( chroot_cmd + "grub-install " + disk )
    os.system( chroot_cmd + "grub-mkconfig -o /boot/grub/grub.cfg" )
#    os.mkdir( "/mnt/boot/efi" )
#    os.system( chroot + " grub-install --target=x86_64-efi --bootloader-id=ArchLinux --efi-directory=/boot" )
#    os.system( chroot + " grub-mkconfig -o /boot/grub/grub.cfg" )
