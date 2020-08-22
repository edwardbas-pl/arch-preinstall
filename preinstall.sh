#!/usr/bin/env bash
#-------------------------------------------------------------------------
#      _          _    __  __      _   _
#     /_\  _ _ __| |_ |  \/  |__ _| |_(_)__
#    / _ \| '_/ _| ' \| |\/| / _` |  _| / _|
#   /_/ \_\_| \__|_||_|_|  |_\__,_|\__|_\__|
#  Arch Linux Post Install Setup and Config
#-------------------------------------------------------------------------

echo "Please enter hostname:"
read hostname
echo "Please enter username:"
read username
echo "Please enter password:"
read -s password
echo "Please repeat password:"
read -s password2
# Check both passwords match
if [ "$password" != "$password2" ]; then
    echo "Passwords do not match"
    exit 1
fi
printf "hostname="$hostname"\n" > "install.conf"
printf "username="$username"\n" > "install.conf"
printf "password="$password"\n" > "install.conf"

echo "-------------------------------------------------"
echo "    Setting up mirrors for optimal download      "
echo "-------------------------------------------------"
timedatectl set-ntp true
pacman -S reflector --noconfirm
cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.old
reflector --verbose --latest 20 --sort rate --save /etc/pacman.d/mirrorlist



echo -e "\nInstalling prereqs...\n$HR"
pacman -S --noconfirm gptfdisk btrfs-progs

echo "-------------------------------------------------"
echo "-------select your disk to format----------------"
echo "-------------------------------------------------"
lsblk
echo "Please enter disk: (example /dev/sda)"
read DISK
echo "--------------------------------------"
echo -e "\nFormatting disk...\n$HR"
echo "--------------------------------------"

mem_quantity=$(grep MemTotal /proc/meminfo | awk '{print $2}')
UNIT=$(grep MemTotal /proc/meminfo | awk '{print $3}')
mem_multipiler=$(echo $(($mem_quantity / 5)))
mem=$(echo $(($mem_multipiler + $mem_quantity)))

#Checking if selected disk is unmounted
umount ${DISK}*
wipefs -fa ${DISK}

# disk prep
sgdisk -Z ${DISK} # zap all on disk
sgdisk -a 2048 -o ${DISK} # new gpt disk 2048 alignment

# create partitions
sgdisk -n 1:0:+1000M ${DISK}
sgdisk -n 3:0:+$mem$UNIT ${DISK} 
sgdisk -n 2:0:     ${DISK} 

BOOT="${DISK}1"
ROOT="${DISK}2"
SWAP="${DISK}3"
:
# set partition types
sgdisk -t 1:ef00 ${DISK}
sgdisk -t 2:8300 ${DISK}
sgdisk -t 3:8200 ${DISK}

# label partitions
sgdisk -c 1:"UEFISYS" $BOOT
sgdisk -c 2:"ROOT" $ROOT
sgdisk -c 2:"SWAP" $SWAP

# make filesystems
echo -e "\nCreating Filesystems...\n$HR"

mkfs.vfat -F32 $BOOT
mkfs.ext4 -L "ROOT" $ROOT
mkswap $SWAP

# mount target
mkdir -p /mnt
mount $ROOT /mnt
mkdir -p /mnt/boot
mount $BOOT /mnt/boot/
swapon $SWAP

echo "--------------------------------------"
echo "-- Arch Install on Main Drive       --"
echo "--------------------------------------"
pacstrap /mnt base base-devel linux linux-firmware vim nano sudo --noconfirm --needed
genfstab -U /mnt >> /mnt/etc/fstab



echo "--------------------------------------"
echo "-- Preparing users locales and other--"
echo "--------------------------------------"

#Setting up User
arch-chroot /mnt useradd -mU -G wheel,uucp,video,audio,storage,games,input $username
echo "$username:$password" | arch-chroot /mnt chpasswd 
echo "root:$password" | arch-chroot /mnt chpasswd  
arch-chroot /mnt usermod -aG wheel,audio,video,optical,storage $username #adding suer to groups
$username:$password | arch-chroot /mnt chpasswd #Seting password to user
# Add sudo no password rights
sed -i 's/^# %wheel ALL=(ALL) NOPASSWD: ALL/%wheel ALL=(ALL) NOPASSWD: ALL/' /mnt/etc/sudoers

#Setting hostname and hosts file
echo $hostname > /mnt/etc/hostname
echo "127.0.0.1   localhost" > /mnt/etc/hosts
echo "::1        	localhost" >> /mnt/etc/hosts
echo "127.0.1.1   $hostname.localdomain $hostname" >> /mnt/etc/hosts

#Setting Locales

echo "LANG=pl_PL.UTF-8" > /mnt/etc/locale.conf
sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /mnt/etc/locale.gen
arch-chroot /mnt locale-gen
arch-chroot /mnt timedatectl --no-ask-password set-timezone Europe/Warsaw
# Set keymaps
arch -chroot /mnt localectl --no-ask-password set-keymap us


    



echo "--------------------------------------"
echo "-- Bootloader Systemd Installation  --"
echo "--------------------------------------"

#setting up systemd bootloader entry
arch-chroot /mnt bootctl --esp-path=/boot install
touch /mnt/boot/loader/loader.conf
echo "default arch-*" > /mnt/boot/loader/loader.conf
touch /mnt/boot/loader/entries/arch.conf
echo "title 	Arch Linux" > /mnt/boot/loader/entries/arch.conf
echo "linux /vmlinuz-linux" >> /mnt/boot/loader/entries/arch.conf
echo "initrd  /initramfs-linux.img" >> /mnt/boot/loader/entries/arch.conf
echo "options root=$ROOT rw" >> /mnt/boot/loader/entries/arch.conf

#setting up makepkg flags
nc=$(grep -c ^processor /proc/cpuinfo)
echo "You have " $nc" cores."
echo "-------------------------------------------------"
echo "Changing the makeflags for "$nc" cores."
sed -i 's/#MAKEFLAGS="-j2"/MAKEFLAGS="-j'$nc'"/g' /mnt/etc/makepkg.conf
echo "Changing the compression settings for "$nc" cores."
sed -i 's/COMPRESSXZ=(xz -c -z -)/COMPRESSXZ=(xz -c -T '$nc' -z -)/g' /mnt/etc/makepkg.conf





echo "Base Networking"
pacstrap /mnt dhcpcd git neofetch
arch-chroot /mnt git clone https://github.com/edwardbas-pl/arch-postinstall /mnt/home/$username/arch-postinstall
arch-chroot /mnt systemctl enable dhcpcd






#umount -R /mnt

echo "--------------------------------------"
echo "--   SYSTEM READY FOR FIRST BOOT    --"
echo "--------------------------------------"