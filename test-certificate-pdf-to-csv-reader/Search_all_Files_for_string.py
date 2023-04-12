import os
from os import walk

mypath = "<PATH>\\"

f = []
for (dirpath, dirnames, filenames) in walk(mypath):
    for name in filenames:
        full = os.path.abspath(dirpath + '\\' + name)
        fullname = os.path.abspath(full)
        f.append(fullname)

substring = "2020"

for item in f:
    if item.endswith(".php"):
        with open(os.path.abspath(item), encoding="UTF-8") as file:
            for l in file:
                if substring in l:
                    print(l, item[59:])


