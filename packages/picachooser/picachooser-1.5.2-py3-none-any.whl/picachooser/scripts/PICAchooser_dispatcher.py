#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#   Copyright 2016-2019 Blaise Frederick
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
# $Author: frederic $
# $Date: 2016/07/11 14:50:43 $
#       $Id: resamp1tc,v 1.12 2016/07/11 14:50:43 frederic Exp $
#


import os
import subprocess
import sys


def main():
    # get the command line parameters
    execdir = sys.path[0]
    validcommands = ["PICAchooser", "grader", "rtgrader", "melodicomp", "xyzzy", "debug"]

    thecommand = sys.argv[1:]
    if thecommand[0] in validcommands:
        # the script exists, now check if it is installed
        fullpathtocommand = os.path.join(execdir, thecommand[0])
        if thecommand[0] == "xyzzy":
            subprocess.call("/bin/bash")
        elif thecommand[0] == "debug":
            print("debug:")
            print(f"\tvalid commands: {validcommands}")
            print(f"\texecdir: {execdir}")
        elif os.path.isfile(fullpathtocommand):
            subprocess.call([fullpathtocommand] + thecommand[1:])
        else:
            print(thecommand[0], "is a PICAchooser script, but is not installed")
    else:
        print(thecommand[0], "is not a script in the PICAchooser package")


def entrypoint():
    main()

if __name__ == "__main__":
    entrypoint()
