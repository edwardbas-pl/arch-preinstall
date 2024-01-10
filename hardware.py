import os
import subprocess


def nvme_check( path:str ) -> bool:
    if "nvme" in path:
        return True
    else:
        return False

def efi_check() -> bool:
    if os.path.exists("/sys/firmware/efi/efivars") == True:
        return True
    else:
        return False

def get_cpu_vendor() -> str:
    cpu = subprocess.getoutput([" grep -m 1 vendor_id /proc/cpuinfo  | awk '{print $3} ' "])
    if "GenuineIntel" in cpu:
        CPU = "INTEL"
    elif "AuthenticAMD" in cpu:
        CPU = "AMD"
    else:
        print("unknown cpu")
        CPU = "unknown"
    return CPU

def get_mem_size() -> str:
    #check ho many ram (in MB) in order to build sufficient swap partition
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_mega_bytes = mem_bytes/(1024.**2) 
    return str(round(mem_mega_bytes))

def get_gpu_vendor() -> str: 
    gpu = subprocess.getoutput([" lspci | grep -i --color 'vga\|3d\|2d' "])
    if "Intel" in gpu:
        gpu = "intel"
    elif "Radeon" in gpu:
        gpu = "amd"
    elif "NV" in gpu:
        gpu = "nvidia"
    return gpu
