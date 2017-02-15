
This directory contains scripts which are meant to made certain actions on the GDAX exchange quick and easy from the terminal.

My current usage model here is to place a bash script called "gdax" in ~/bin, with the following contents:

    #!/bin/bash
    ~/[path]/[to]/[repo]/eth/script/${1}.py ${@:2}

Then the scripts can be executed as though they were sub-commands of "gdax".

For example:  gdax order list --details

Otherwise, the scripts can be invoked on their own as usual (e.g.  "./order.py list --details")
