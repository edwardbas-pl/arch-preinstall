#!/bin/bash

echo "-------------------------------------------------"
echo "-------select your disk to format----------------"
echo "-------------------------------------------------"
lsblk
echo "Please enter disk: (example /dev/sda)"
read DISK

echo "--------------------------------------"
echo -e "\nFormatting disk...\n$HR"
echo "--------------------------------------"

#This segment check how much ram do you have instaled in your system and creates little bit bigger swap partition
echo "Memory chceck debug"
mem_quantity=$(grep MemTotal /proc/meminfo | awk '{print $2}')
UNIT=$(grep MemTotal /proc/meminfo | awk '{print $3}')
mem_multipiler=$(echo $(($mem_quantity / 9)))
mem=$(echo $(($mem_multipiler + $mem_quantity)))
echo $mem_quantity
echo $UNIT
echo $mem_multipiler
echo $mem
read pause

#Checking if selected disk is unmounted
umount ${DISK}/*


# disk prep
sgdisk -Z ${DISK} # zap all on disk
sgdisk -a 2048 -o ${DISK} # new gpt disk 2048 alignment

# create partitions
sgdisk -n 1:0:+1000M ${DISK}
sgdisk -n 3:0:+$mem$UNIT ${DISK} 
sgdisk -n 2:0:     ${DISK} 

#This if statement check drive type because nvme partisions ar named with letter p before partiton
if [[ -d "/sys/firmware/efi/efivars" ]]
then

	sgdisk -a 2048 -o ${DISK} # new gpt disk 2048 alignment
	if [[ ${DISK} == *nvme* ]];
	then
		echo "your disc standard is nvme"

		export BOOT="${DISK}p1"
		export ROOT="${DISK}p2"
		export SWAP="${DISK}p3"
	else
		echo "your disc standard is SATA"
		export BOOT="${DISK}1"
		export ROOT="${DISK}2"
		export SWAP="${DISK}3"
	fi
	# create partitions
	sgdisk -n 1:0:+1000M ${DISK}
	sgdisk -n 3:0:+$mem$unit ${DISK} 
	sgdisk -n 2:0:     ${DISK} 

	# set partition types
	sgdisk -t 1:ef00 ${DISK}
	sgdisk -t 2:8300 ${DISK}
	sgdisk -t 3:8200 ${DISK}

	# label partitions
	sgdisk -c 1:"UEFISYS" $BOOT
	sgdisk -c 2:"ROOT" $ROOT

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




else	#if booted in legacy mode
	wipefs -fa ${DISK}
	if [[ ${DISK} == *nvme* ]];
	then
		echo "your disc standard is nvme"

		export ROOT="${DISK}p1"
		export SWAP="${DISK}p2"
	else
		echo "your disc standard is SATA"
		export ROOT="${DISK}1"
		export SWAP="${DISK}2"
	fi

	(
		echo o
		echo n
		echo p
		echo 1
		echo
		echo -${mem}K
		echo t
		echo 8
		echo 2
		echo w
	) | fdisk ${DISK}
	(
		echo n
		echo p
		echo 2
		echo
		echo
		echo w
	) | fdisk ${DISK}

	# make filesystems
	echo -e "\nCreating Filesystems...\n$HR"

	mkfs.ext4 -L "ROOT" $ROOT
	mkswap $SWAP

	# mount target
	mkdir -p /mnt
	mount $ROOT /mnt
	swapon $SWAP
fi


