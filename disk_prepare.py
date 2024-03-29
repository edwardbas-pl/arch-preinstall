import os

def list_disk() -> None:
    os.system('lsblk --nodeps')
    

def efi_partitioning( DISK:str , PARTITION_LIST:str , swap_size:str ) -> int:
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
    os.system("mkdir -p /mnt/boot")
    os.system("mount " + BOOT + " /mnt/boot ")



def legacy_partitioning( DISK:str , PARTITION_LIST:str , swap_size:str ) -> None:
    #creating partitions
    ROOT = PARTITION_LIST[0]
    SWAP = PARTITION_LIST[1]
    # os.system( "wipefs -fa " + DISK )
    os.system("sgdisk -Z " + DISK) #zap all on disk
    root_partition_steps = "( echo o; echo n; echo p; echo 1; echo; echo -" + swap_size + "M; echo t; echo 83; echo w  ) | fdisk " + DISK 
    print(root_partition_steps)
    os.system(root_partition_steps)
    os.system("( echo n; echo p; echo 2; echo; echo; echo w ) | fdisk " + DISK)

    #formating partitions
    os.system('echo y | mkfs.ext4 ' + ROOT)
    os.system('mkswap ' + SWAP)

    #mounting partitions
    os.system('swapon ' + SWAP)
    os.system("mount " + ROOT + " /mnt ")

#TODO need to meke thi to perform only one action
def prepare_disks( is_efi:bool , swap_size:str , disk:str ) -> list:
    partition_list = set_disk_variables(disk,is_efi)
    if len(partition_list) == 3:
        efi_partitioning( disk , partition_list , swap_size )
        pass
    elif len(partition_list) == 2:
        legacy_partitioning( disk , partition_list , swap_size )
        pass
    print(len(partition_list))
    return partition_list
    

def set_disk_variables( disk:str , is_efi:bool ) -> list:
    partitions_list = []
    if  is_efi == True:
        if "nvme" in disk:
            partitions_list.append(disk + "p1")
            partitions_list.append(disk + "p2")
            partitions_list.append(disk + "p3")
        else:
            partitions_list.append(disk + "1")
            partitions_list.append(disk + "2")
            partitions_list.append(disk + "3")
    else:
        if "nvme" in disk:
            partitions_list.append(disk + "p1")
            partitions_list.append(disk + "p2")
        else:
            partitions_list.append(disk + "1")
            partitions_list.append(disk + "2")
    return partitions_list
