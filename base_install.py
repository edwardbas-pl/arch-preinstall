import os

def install( strap_cmd , component_list ) -> None:
#    for i in component_list:
#        os.system( strap_cmd + i )
#        pass
    os.system( strap_cmd + ' ' + ' '.join(component_list))
    genfstab()

def genfstab() -> None:
    os.system( "genfstab -U /mnt >> /mnt/etc/fstab")

def host_settings( hostname:str ) -> None:
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

def user_setup( CHROOT:str , username:str , password:str ) -> None:
    os.system( CHROOT + " useradd -m " + username )
    os.system( CHROOT + " usermod -aG wheel,uucp,video,audio,storage,games,input " + username )
    os.system( "echo " + username + ":" + password  + " | " + CHROOT + " chpasswd")
    os.system( "echo 'root:" + password + "' | " + CHROOT + " chpasswd" )
    os.system( CHROOT + " usermod -aG wheel,audio,video,optical,storage " + username )
    #os.system( "chmod +w /mnt/etc/sudoers" )
    #os.system( CHROOT + " sed -i 's/^# %wheel ALL=(ALL) NOPASSWD: ALL/%wheel ALL=(ALL) NOPASSWD: ALL/' /etc/sudoers" )
    #os.system( "chmod +w /mnt/etc/sudoers" )
    #os.system( "echo  '%wheel ALL=(ALL) NOPASSWD: ALL' >> /mnt/etc/sudoers" )
    with open('/mnt/etc/sudoers.d/user', 'w+') as f:
        f.write('%wheel ALL=(ALL) NOPASSWD: ALL\n')
    #os.system( "chmod -w /mnt/etc/sudoers.d/user" )
    # os.system( "chmod -w /mnt/etc/sudoers" )

def set_locale( CHROOT:str ) -> None:
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

def systemDboot( chroot_cmd:str , partition_list:str , cpu:str ) -> None:
    root = partition_list[1]
    swap = partition_list[2]
    os.system( chroot_cmd + " bootctl --esp-path=/boot install" )
    #os.system( " touch /mnt/boot/loader/loader.conf " )
    os.system("mkdir -p /mnt/boot/loader/entries")
    f = open( "/mnt/boot/loader/loader.conf" , "w+" )
    f.write( "default\t\tarch-*\n" )
    f.close()
    f = open( "/mnt/boot/loader/entries/arch.conf" , "w+" )
    f.write( "title\t\tArch Linux\n" )
    f.write( "linux\t\t/vmlinuz-linux\n" )
    if cpu == "INTEL":
        f.write("initrd\t\t/intel-ucode.img\n")
    elif cpu == "AMD":
        f.write("initrd\t\t/amd-ucode.img\n")
    f.write( "initrd\t\t/initramfs-linux.img\n" )
    f.write( "options\t\troot=" + root + " rw resume=" + swap )
    f.close()

def grub_install( chroot_cmd:str ) -> None:
    os.mkdir( "/mnt/boot/efi" )
    os.system( chroot + " grub-install --target=x86_64-efi --bootloader-id=ArchLinux --efi-directory=/boot" )
    os.system( chroot + " grub-mkconfig -o /boot/grub/grub.cfg" )
