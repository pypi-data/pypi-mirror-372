# :tv: pytntprog

pytntprog displays the program of tnt tv in France


# 💫 demo

![demo](https://user-images.githubusercontent.com/45128847/137587565-c2dc81ef-95ca-4312-89ae-e9085ac964c7.gif)

# 🚀 How use **pytntprog**

- ``pytntprog`` display the tnt programm for the current day with id index
- ``pytntprog -h`` show the help message
- ``pytntprog -i [id]`` display the details of the programm with id
- ``pytntprog -c`` display current programm
- ``pytntprog -l [INT]`` filter programm with minimal length in minutes
- ``pytntprog -a`` display all tnt programm (current day by default)
- ``pytntprog -f "TF1"`` display the tnt programm for the current day with filter TF1
- ``pytntprog -f "Stade 2" "France 3"`` display the tnt programm for the current day with filter Stade 2 + France 3
- ``pytntprog -F "sport"`` display the tnt programm for the current day with agressive filter "sport" (description and resume)
- ``pytntprog -C`` or ``pytntprog --chache`` download the distant xml file event if the cache is not finished (24h by default)
- ``pytntprog -u`` to update pytntprog

If you add ``--nocolor/-n`` option, you disable the colors in sysout

# :gear: Install

See [this page](INSTALL.md)

# :construction_worker: Contribution

See [this page](CONTRIBUTING.md)

# :package: Changelog


See [this page](CHANGELOG.md)

# :pencil: License

MIT License

Copyright (c) 2021 [thib1984](https://github.com/thib1984)

See [this page](LICENSE.txt) for details