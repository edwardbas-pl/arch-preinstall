import psutil

boot = ""
root = ""
swap = "" 

def list_disk():                                                  
	drps = psutil.disk_partitions()                           
	drives = [dp.device for dp in drps ]
	for i in drives:                                          
	    print( i )

def get():
    print("type in")
    cos = input()
    return str(cos)


def set(dysk):
    global boot
    global root
    global swap
    boot = dysk + '1'
    root = dysk + '2'
    swap = dysk + '3'

list_disk()
xd = get()
set(xd)

print(boot)
print(root)
print(swap)

