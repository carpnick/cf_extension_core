""" Add Paths to make it so unit tests work """

# Fix the tests so the imports work
# Basically we are appending the source folder to the path so we can properly test the python code.
# Is there a better way to do this?

import os
import sys
top_level_folder = os.getcwd() + os.sep + "src"
sub_dirs = [os.path.join(top_level_folder, o) for o in os.listdir(top_level_folder) if os.path.isdir(os.path.join(top_level_folder, o))]

for dir_to_add in sub_dirs:
    #print(dir_to_add)
    sys.path.append(dir_to_add)

sys.path.append(top_level_folder)