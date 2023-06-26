import os

import constants


# Function To Clear out The temp Directory
def clear_temp():
    # Get all the Files from the Temp Directory
    print("Getting Files from the Temp Directory...")
    files = os.listdir(constants.temp_folder)

    # Deleting all the files
    print("Clearing the Temp Directory...")
    for file in files:
        os.remove(constants.temp_folder + "/" + file)
    return

# clear_temp(r"C:\Users\Delay\Desktop\projects\Pylit2.0\src\tests\temp")
