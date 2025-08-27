#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#   Copyright 2020 Blaise Frederick
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
# $Id: tidepool,v 1.28 2016/07/11 14:50:43 frederic Exp $
#
# -*- coding: utf-8 -*-

"""
A simple GUI for rating timecoursese by whatever metric you want
"""

import argparse
import os
import sys

import numpy as np
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy.stats import pearsonr

import picachooser.colormaps as cm
import picachooser.io as io
import picachooser.LightboxItem as lb
import picachooser.util as pica_util

try:
    from PyQt6.QtCore import QT_VERSION_STR
except ImportError:
    pyqtversion = 5
else:
    pyqtversion = 6

# fix for Big Sur on macOS
os.environ["QT_MAC_WANTS_LAYER"] = "1"


class KeyPressWindow(QtWidgets.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    sigResize = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def closeEvent(self, event):
        writecorrespondence()

    def keyPressEvent(self, ev):
        self.sigKeyPress.emit(ev)

    def resizeEvent(self, ev):
        self.sigResize.emit(ev)


def selectsort():
    global sorttype, sortnames, indexmap, thecorrcoeffs

    print("setting sort type to", sortnames[sorttype])

    if sortnames[sorttype] == "file 1 order":
        indexmap = sorted(indexmap)
    elif sortnames[sorttype] == "correlation coefficient":
        # print(thecorrcoeffs)
        indexmap = [x for _, x in sorted(zip(thecorrcoeffs, indexmap), reverse=True)]
    else:
        print("illegal sort type")

    print(indexmap)

    updateTCinfo()
    updateLightboxes()


def incrementsorttype():
    global sorttype, sortnames

    sorttype = (sorttype + 1) % len(sortnames)
    selectsort()


def decrementsorttype():
    global sorttype, sortnames

    sorttype = (sorttype - 1) % len(sortnames)
    selectsort()


def writecorrespondence():
    global alldata1, numelements1, Correspondancefile, indexmap, thecorrcoeffs

    outputlist = ["idx1\tidx2\tcorrcoeff"]
    for idx in range(numelements1):
        componentindex1 = indexmap[idx]
        thiscomponent1 = alldata1[namelist1[componentindex1]]
        componentindex2 = thiscomponent1["bestmatch"]
        outputlist.append(
            f"{componentindex1}\t{componentindex2}\t{thecorrcoeffs[componentindex1]}"
        )
    outputstring = "\n".join(outputlist)
    with open(Correspondancefile, "w") as thefile:
        thefile.write(outputstring + "\n")


def windowResized(evt):
    global lbwin1, lbwin2, verbose

    if verbose:
        print("handling window resize")

    if lbwin1 is not None and lbwin2 is not None:
        updateLightboxes()


def keyPressed(evt):
    global whichcomponent, numelements1, lbwin1, lbwin2, verbose, domotion, dotimecourse
    global leftinfo, rightinfo, blinkstatus

    if verbose:
        print("processing keypress event")

    if evt.key() == QtCore.Qt.Key.Key_Up:
        incrementsorttype()
    elif evt.key() == QtCore.Qt.Key.Key_Down:
        decrementsorttype()
    elif evt.key() == QtCore.Qt.Key.Key_Left:
        whichcomponent = (whichcomponent - 1) % numelements1
        print("IC set to:", whichcomponent + 1)
    elif evt.key() == QtCore.Qt.Key.Key_Right:
        whichcomponent = (whichcomponent + 1) % numelements1
        print("IC set to:", whichcomponent + 1)
    elif evt.key() == QtCore.Qt.Key.Key_A:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("ax")
            thewin.resetWinProps()
        print("Setting orientation to axial")
    elif evt.key() == QtCore.Qt.Key.Key_C:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("cor")
            thewin.resetWinProps()
        print("Setting orientation to coronal")
    elif evt.key() == QtCore.Qt.Key.Key_S:
        for thewin in [lbwin1, lbwin2]:
            thewin.setorient("sag")
            thewin.resetWinProps()
        print("Setting orientation to sagittal")
    elif evt.key() == QtCore.Qt.Key.Key_D:
        print("Dumping main window information")
        for thewin in [lbwin1, lbwin2]:
            thewin.printWinProps()
    elif evt.key() == QtCore.Qt.Key.Key_B:
        print("Blinking")
        blinkstatus = not blinkstatus
        if blinkstatus:
            lbwin1.setviewinfo(rightinfo)
            lbwin2.setviewinfo(leftinfo)
        else:
            lbwin1.setviewinfo(leftinfo)
            lbwin2.setviewinfo(rightinfo)
    elif evt.key() == QtCore.Qt.Key.Key_R:
        whichcomponent = 0
    elif evt.key() == QtCore.Qt.Key.Key_Escape:
        writecorrespondence()
        print("correspondence file written")
    else:
        print(evt.key())

    updateTCinfo()
    updateLightboxes()


def updateTCinfo():
    global whichcomponent, indexmap, sorttype, sortnames, blinkstatus
    global alldata1, alldata2, namelist1, namelist2, win, numelements1, numelements2, verbose

    if verbose:
        print("entering updateTCinfo")
    componentindex1 = indexmap[whichcomponent]
    thiscomponent1 = alldata1[namelist1[componentindex1]]
    componentindex2 = thiscomponent1["bestmatch"]
    thiscomponent2 = alldata2[namelist2[thiscomponent1["bestmatch"]]]
    pane1title = alldata1[
        "filelabel"
    ] + ": IC {0} of {1}: {2:.2f}% explained var., {3:.2f}% total var.".format(
        componentindex1 + 1,
        numelements1,
        thiscomponent1["explainedvar"],
        thiscomponent1["totalvar"],
    )
    pane2title = alldata2[
        "filelabel"
    ] + ": IC {0} of {1}: {2:.2f}% explained var., {3:.2f}% total var.".format(
        componentindex2 + 1,
        numelements2,
        thiscomponent2["explainedvar"],
        thiscomponent2["totalvar"],
    )

    if blinkstatus:
        ui.pane1_label.setText(pane2title)
        ui.pane2_label.setText(pane1title)
    else:
        ui.pane1_label.setText(pane1title)
        ui.pane2_label.setText(pane2title)

    win.setWindowTitle(f"melodicomp: sorting by {sortnames[sorttype]}")


def updateLightboxes():
    global lbwin1, lbwin2, whichcomponent, indexmap, verbose, alldata1, alldata2, namelist1, namelist2
    global keepcolor, discardcolor, thecorrthresh

    if verbose:
        print("entering updateLightboxes")

    componentindex1 = indexmap[whichcomponent]
    thiscomponent1 = alldata1[namelist1[componentindex1]]
    componentindex2 = thiscomponent1["bestmatch"]

    thelabel1 = f"{alldata1['filelabel']} IC {namelist1[componentindex1]}"
    thelabel2 = f"{alldata2['filelabel']} IC {namelist2[componentindex2]}: correlation with {alldata1['filelabel']} is {thiscomponent1['bestcorr']:.3f}"
    if thiscomponent1["bestcorr"] >= thecorrthresh:
        thecolor = config["keepcolor"]
    else:
        thecolor = config["discardcolor"]
        thelabel2 += " (below threshold)"
    lbwin1.setTpos(componentindex1)
    lbwin2.setTpos(componentindex2)
    for thewin in [lbwin1, lbwin2]:
        thewin.getWinProps()
        thewin.resetWinProps()
    lbwin1.setLabel(thelabel1, thecolor)
    lbwin2.setLabel(thelabel2, thecolor)

    # ui.correlation_label.setText("thecorrcoeff")


def main():
    global ui, win, lbwin1, lbwin2
    global namelist1, namelist2, Correspondancefile, alldata1, alldata2, motion, whichcomponent
    global indexmap, sorttype, sortnames, thecorrcoeffs, numelements1, numelements2
    global verbose
    global config
    global leftinfo, rightinfo, blinkstatus
    global Funcfile, Mixfile, filteredfile
    global domotion, dotimecourse
    global thecorrthresh

    lbwin1 = None
    lbwin2 = None
    verbose = False
    domotion = True
    dotimecourse = True

    parser = argparse.ArgumentParser(
        prog="melodicomp",
        description="A program to compare two sets of melodic components.",
        usage="%(prog)s ICfile1 ICfile2 [options]",
    )

    # Required arguments
    parser.add_argument(
        "ICfile1",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The first IC component file.  This will be the exemplar, and for each component, the closest component in ICfile2 will be "
            "selected for comparison. "
        ),
        default=None,
    )
    parser.add_argument(
        "ICfile2",
        action="store",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The second IC component file.  Components in this file will be selected to match components in ICfile1. "
        ),
        default=None,
    )

    llfilespec = parser.add_argument_group(
        "Nonstandard input file location specification.  Setting these overrides the locations assumed from ICfile1."
    )
    llfilespec.add_argument(
        "--backgroundfile",
        dest="specBGfile",
        metavar="BGFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The anatomic file on which to display the ICs (by default assumes a file called 'mean.nii.gz' in the "
            "same directory as ICfile1.))"
        ),
        default=None,
    )
    llfilespec.add_argument(
        "--maskfile",
        dest="specICmask",
        metavar="ICMASK",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The independent component mask file produced by MELODIC (by default assumes a file called 'mask.nii.gz' "
            "in the same directory as ICfile1.)"
        ),
        default=None,
    )
    llfilespec.add_argument(
        "--ICstatsfile1",
        dest="melodicICstatsfile1",
        metavar="STATSFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The melodic stats file (by default called 'melodic_ICstats' in the same directory as ICfile1),"
        ),
        default=None,
    )
    llfilespec.add_argument(
        "--ICstatsfile2",
        dest="melodicICstatsfile2",
        metavar="STATSFILE",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help=(
            "The melodic stats file (by default called 'melodic_ICstats' in the same directory as ICfile2),"
        ),
        default=None,
    )

    # optional arguments
    other = parser.add_argument_group("Other arguments")
    other.add_argument(
        "--corrthresh",
        type=lambda x: pica_util.is_float(parser, x),
        help="z threshold for the displayed ICA components.  Default is 2.3.",
        default=0.5,
    )
    other.add_argument(
        "--outputfile",
        type=str,
        help=(
            "Where to write the list of corresponding components (default is 'correspondingcomponents.txt' "
            "in the same directory as ICfile1"
        ),
        default=None,
    )
    # other.add_argument(
    #    "--sortedfile",
    #    metavar="SORTEDFILE",
    #    type=str,
    #    help=(
    #        "Save the components in ICfile2, sorted to match the components of ICfile1, in the file SORTEDFILE."
    #    ),
    #    default=None,
    # )
    other.add_argument(
        "--spatialroi",
        dest="spatialroi",
        type=int,
        nargs=6,
        metavar=("XMIN", "XMAX", "YMIN", "YMAX", "ZMIN", "ZMAX"),
        help=(
            "Only read in image data within the specified ROI.  Set MAX to -1 to go to the end of that dimension."
        ),
        default=(0, -1, 0, -1, 0, -1),
    )
    other.add_argument(
        "--displaythresh",
        type=lambda x: pica_util.is_float(parser, x),
        help="z threshold for the displayed ICA components.  Default is 2.3.",
        default=2.3,
    )
    other.add_argument(
        "--label1",
        type=str,
        help="Label to give to file 1 components in display.  Default is 'File 1'.",
        default="File 1",
    )
    other.add_argument(
        "--label2",
        type=str,
        help="Label to give to file 2 components in display.  Default is 'File 2'.",
        default="File 2",
    )

    misc = parser.add_argument_group("Miscellaneous arguments")
    misc.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {pica_util.version()[0]}",
    )
    misc.add_argument(
        "--detailedversion",
        action="version",
        version=f"%(prog)s {pica_util.version()}",
    )

    debugging = parser.add_argument_group("Debugging arguments")
    debugging.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Output exhaustive amounts of information about the internal workings of melodicomp. "
            "You almost certainly don't want this."
        ),
        default=False,
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Use --help option for detailed information on options.")
        raise

    # make sure we can find the required input files
    # first see if there are specific overrides
    BGfile = args.specBGfile
    ICmask = args.specICmask
    melodicICstatsfile1 = args.melodicICstatsfile1
    melodicICstatsfile2 = args.melodicICstatsfile2

    melodicdir1 = os.path.dirname(args.ICfile1)
    melodicdir2 = os.path.dirname(args.ICfile2)

    thecorrthresh = args.corrthresh

    if BGfile is None:
        BGfile = os.path.join(melodicdir1, "mean.nii.gz")
    if not os.path.isfile(BGfile):
        print("cannot find background file at", BGfile)
        sys.exit()

    if ICmask is None:
        ICmask = os.path.join(melodicdir1, "mask.nii.gz")
    if not os.path.isfile(ICmask):
        print("cannot find independent component mask file at", ICmask)
        sys.exit()

    if melodicICstatsfile1 is None:
        melodicICstatsfile1 = os.path.join(melodicdir1, "melodic_ICstats")
    else:
        melodicICstatsfile1 = melodicICstatsfile1

    if melodicICstatsfile2 is None:
        melodicICstatsfile2 = os.path.join(melodicdir2, "melodic_ICstats")
    else:
        melodicICstatsfile2 = melodicICstatsfile2

    if BGfile is None:
        print("Cannot set background file. ")
        sys.exit()

    if ICmask is None:
        print("Cannot set IC mask. ")
        sys.exit()

    if args.outputfile is not None:
        Correspondancefile = args.outputfile
    else:
        Correspondancefile = os.path.join(melodicdir1, "correspondingcomponents.txt")
    if not os.path.isfile(Correspondancefile):
        initfileexists = True
    else:
        initfileexists = False

    if verbose:
        print(f"ICfile1: {args.ICfile1}")
        print(f"ICfile2: {args.ICfile2}")
        print(f"ICmask: {ICmask}")
        print(f"BGfile: {BGfile}")
        print(f"Correspondancefile: {Correspondancefile}")

    # set the configurable options
    def initconfig():
        print("initializing preferences")
        config = {
            "prefsversion": 1,
            "keepcolor": "g",
            "discardcolor": "r",
        }
        return config

    configfile = os.path.join(os.environ["HOME"], ".melodicomp.json")
    if not os.path.isfile(configfile):
        config = initconfig()
        io.writedicttojson(config, configfile, sort_keys=False)
    else:
        config = io.readdictfromjson(configfile)
        try:
            prefsversion = config["prefsversion"]
        except KeyError:
            prefsversion = 0
        if prefsversion < 1:
            config = initconfig()
            io.writedicttojson(config, configfile)

    # read in the information for both datasets
    alldata1 = {}
    alldata2 = {}
    alldata1["filelabel"] = args.label1
    alldata2["filelabel"] = args.label2

    dummy, numelements1 = io.fmritimeinfo(args.ICfile1)
    dummy, numelements2 = io.fmritimeinfo(args.ICfile2)

    # read in the variance percents
    melodicICstats1 = io.readvecs(melodicICstatsfile1)
    melodicICstats2 = io.readvecs(melodicICstatsfile2)

    # calculate the correlations and pick the best matches
    thecorrelations, thebestmatches = pica_util.calccorrs(
        args.ICfile1, args.ICfile2, ICmask, debug=True
    )
    if thecorrelations is None:
        sys.exit()
    thecorrcoeffs = np.zeros((numelements1), dtype=np.float64)

    namelist1 = []
    print("reading info on ICfile1...")
    for idx in range(numelements1):
        theIC = str(idx + 1)
        namelist1.append(theIC)
        alldata1[theIC] = {}

        alldata1[theIC]["totalvar"] = melodicICstats1[1, idx]
        alldata1[theIC]["explainedvar"] = melodicICstats1[0, idx]
        alldata1[theIC]["bestmatch"] = thebestmatches[idx]
        alldata1[theIC]["bestcorr"] = thecorrelations[idx, thebestmatches[idx]]
        thecorrcoeffs[idx] = thecorrelations[idx, thebestmatches[idx]]
    print("Read in", numelements1, "ICs")
    namelist2 = []
    print("reading info on ICfile2...")
    for idx in range(numelements2):
        theIC = str(idx + 1)
        namelist2.append(theIC)
        alldata2[theIC] = {}

        alldata2[theIC]["totalvar"] = melodicICstats2[1, idx]
        alldata2[theIC]["explainedvar"] = melodicICstats2[0, idx]
    print("Read in", numelements2, "ICs")
    whichcomponent = 0
    indexmap = np.arange(0, numelements1, dtype=int)
    sorttype = 0
    sortnames = ["file 1 order", "correlation coefficient"]

    # make the main window
    if pyqtversion == 5:
        import picachooser.melodicompTemplate as uiTemplate
    else:
        import picachooser.melodicompTemplate_qt6 as uiTemplate

    app = QtWidgets.QApplication([])
    print("setting up output window")
    win = KeyPressWindow()
    win.sigKeyPress.connect(keyPressed)
    win.sigResize.connect(windowResized)

    ui = uiTemplate.Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    win.setWindowTitle("melodicomp")

    print("setting up image windows")
    geommaskimage = lb.imagedataset(
        "ICmask",
        ICmask,
        "ICmask",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.mask_state,
    )
    fgimage1 = lb.imagedataset(
        "IC",
        args.ICfile1,
        "IC",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.redyellow_state,
        geommask=geommaskimage.data,
    )
    fgimage1.setFuncMaskByThresh(threshval=args.displaythresh)
    fgimage2 = lb.imagedataset(
        "IC",
        args.ICfile2,
        "IC",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.redyellow_state,
        geommask=geommaskimage.data,
    )
    fgimage2.setFuncMaskByThresh(threshval=args.displaythresh)

    bgimage = lb.imagedataset(
        "BG",
        BGfile,
        "background",
        xlims=args.spatialroi[0:2],
        ylims=args.spatialroi[2:4],
        zlims=args.spatialroi[4:6],
        lut_state=cm.gray_state,
    )
    lbwin1 = lb.LightboxItem(fgimage1, ui.image_graphicsView_1, bgmap=bgimage, verbose=verbose)
    leftinfo = lbwin1.getviewinfo()
    lbwin2 = lb.LightboxItem(fgimage2, ui.image_graphicsView_2, bgmap=bgimage, verbose=verbose)
    rightinfo = lbwin2.getviewinfo()
    blinkstatus = False

    # initialize everything
    updateTCinfo()
    updateLightboxes()

    QtWidgets.QApplication.instance().exec()


def entrypoint():
    main()


if __name__ == "__main__":
    entrypoint()
