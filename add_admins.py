# Script to add administrators to application.

from route_funcs import Session
from sys import argv, exit, stderr
import profile_funcs as prof

def main():
    """Adds user with given netid as an admin
    """


    # get netid
    if len(argv) != 2:
        print("Usage: add_admins.py netid")
        print("Error: Too many arguments", file=stderr)
        exit(1)

    netid = argv[1]

    try:
        netid = str(netid)
    except Exception as ex:
        print("Error parsing netid " + str(ex), file=stderr)
        exit(1)

    is_admin = True
    # update admin status if necessary
    if prof.user_exists(netid):
        if prof.is_admin(netid):
            print("%s is already an admin." % netid)
            return
        else:
            success = prof.update_admin_status(netid, is_admin) # error handling: need to change profile_funcs to use try/except
    # otherwise add user as an admin
    else:
        success = prof.add_user(netid, is_admin) # error handling see above comment

    if success != 0:
        print("Error occured while adding %s as admin." % netid)

if __name__ == '__main__':
    main()