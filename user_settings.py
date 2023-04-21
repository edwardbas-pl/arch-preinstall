import getpass

def get_username( username:str = None ) -> str:
    if username == None:
        print("Username: ")
        username = str(input())
    else:
        pass
    return username

def get_hostname( hostname:str = None ) -> str:
    if hostname == None:
        hostname = str(input("Enter Hostname: "))
    else:
        pass
    return hostname

def get_password( password:str = None ) -> str:
    if password == None:
        password = getpass.getpass()
        second_password = getpass.getpass("retype password")
        if password == second_password:
            print("password does match")
        elif password != second_password:
            print("passwords doesnt match... Try Again")
            password = get_password()
    return password
