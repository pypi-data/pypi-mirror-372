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
import glob
import os
import sys

import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy import fftpack

import picachooser.LightboxItem as lb
import picachooser.util as pica_util

try:
    from PyQt6.QtCore import QT_VERSION_STR
except ImportError:
    pyqtversion = 5
else:
    pyqtversion = 6

hammingwindows = {}


def hamming(length, debug=False):
    #   return 0.54 - 0.46 * np.cos((np.arange(0.0, float(length), 1.0) / float(length)) * 2.0 * np.pi)
    r"""Returns a Hamming window function of the specified length.  Once calculated, windows
    are cached for speed.

    Parameters
    ----------
    length : int
        The length of the window function
        :param length:

    debug : boolean, optional
        When True, internal states of the function will be printed to help debugging.
        :param debug:

    Returns
    -------
    windowfunc : 1D float array
        The window function
    """
    try:
        return hammingwindows[str(length)]
    except KeyError:
        hammingwindows[str(length)] = 0.54 - 0.46 * np.cos(
            (np.arange(0.0, float(length), 1.0) / float(length)) * 2.0 * np.pi
        )
        if debug:
            print("initialized hamming window for length", length)
        return hammingwindows[str(length)]


def spectrum(inputdata, Fs=1.0, mode="power", trim=True):
    r"""Performs an FFT of the input data, and returns the frequency axis and spectrum
    of the input signal.

    Parameters
    ----------
    inputdata : 1D numpy array
        Input data
        :param inputdata:

    Fs : float, optional
        Sample rate in Hz.  Defaults to 1.0
        :param Fs:

    mode : {'real', 'imag', 'mag', 'phase', 'power'}, optional
        The type of spectrum to return.  Default is 'power'.
        :param mode:

    trim: bool
        If True (default) return only the positive frequency values

    Returns
    -------
    specaxis : 1D float array
        The frequency axis.

    specvals : 1D float array
        The spectral data.

    Other Parameters
    ----------------
    Fs : float
        Sample rate in Hz.  Defaults to 1.0
        :param Fs:

    mode : {'real', 'imag', 'complex', 'mag', 'phase', 'power'}
        The type of spectrum to return.  Legal values are 'real', 'imag', 'mag', 'phase', and 'power' (default)
        :param mode:
    """
    if trim:
        specvals = fftpack.fft(inputdata)[0 : len(inputdata) // 2]
        maxfreq = Fs / 2.0
        specaxis = np.linspace(0.0, maxfreq, len(specvals), endpoint=False)
    else:
        specvals = fftpack.fft(inputdata)
        maxfreq = Fs
        specaxis = np.linspace(0.0, maxfreq, len(specvals), endpoint=False)
    if mode == "real":
        specvals = specvals.real
    elif mode == "imag":
        specvals = specvals.imag
    elif mode == "complex":
        pass
    elif mode == "mag":
        specvals = np.absolute(specvals)
    elif mode == "phase":
        specvals = np.angle(specvals)
    elif mode == "power":
        specvals = np.sqrt(np.absolute(specvals))
    else:
        print("illegal spectrum mode")
        specvals = None
    return specaxis, specvals


class KeyPressWindow(QtWidgets.QMainWindow):
    sigKeyPress = QtCore.pyqtSignal(object)
    sigResize = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, ev):
        self.sigKeyPress.emit(ev)

    def resizeEvent(self, ev):
        self.sigResize.emit(ev)


def incrementgrade(whichfile):
    global alldata, namelist

    alldata[namelist[whichfile]]["grade"] += 1


def decrementgrade(whichfile):
    global alldata, namelist

    alldata[namelist[whichfile]]["grade"] -= 1


def writegrades():
    global alldata, namelist, numelements, outputfile

    with open(outputfile, "w") as thefile:
        for i in range(len(namelist)):
            thefile.write(
                "{0}, {1:d}, {2:f}\n".format(
                    namelist[i],
                    alldata[namelist[i]]["grade"],
                    alldata[namelist[i]]["samplerate"],
                )
            )


def windowResized(evt):
    global mainwin

    print("handling window resize")
    if mainwin is not None:
        updateLightbox()


def keyPressed(evt):
    global whichfile, numelements, mainwin

    if evt.key() == QtCore.Qt.Key.Key_Up:
        incrementgrade(whichfile)
    elif evt.key() == QtCore.Qt.Key.Key_Down:
        decrementgrade(whichfile)
    elif evt.key() == QtCore.Qt.Key.Key_Left:
        whichfile = (whichfile - 1) % numelements
    elif evt.key() == QtCore.Qt.Key.Key_Right:
        whichfile = (whichfile + 1) % numelements
    elif evt.key() == QtCore.Qt.Key.Key_Escape:
        writegrades()
        print("done")
    else:
        print(evt.key())

    updateTimecourse()
    if mainwin is not None:
        updateLightbox()


def updateTimecourse():
    global timecourse_ax, spectrum_ax, whichfile, alldata, namelist, win, numelements
    thisfile = alldata[namelist[whichfile]]
    windowtitle = "Grader - {0} ({1} of {2})".format(namelist[whichfile], whichfile, numelements)
    win.setWindowTitle(windowtitle)

    if thisfile["grade"] is None:
        pencolor = "w"
    elif thisfile["grade"] == 0:
        pencolor = "w"
    elif thisfile["grade"] > 0:
        pencolor = "g"
    else:
        pencolor = "r"

    timecourse_ax.plot(
        thisfile["timeaxis"],
        thisfile["timecourse"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=1),
        clear=True,
    )

    if thisfile["grade"] is None:
        thelabel = "Grade: None"
    else:
        thelabel = "Grade: {0}".format(thisfile["grade"])

    spectrum_ax.plot(
        thisfile["freqaxis"],
        thisfile["spectrum"],
        name=thelabel,
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=1),
        clear=True,
    )

    spectop = 1.25 * np.max(thisfile["spectrum"])
    spectrum_ax.setYRange(0.0, spectop, padding=0)

    # text = pg.TextItem(text=thelabel,
    #                   anchor = (0.0, 1.0),
    #                   angle = 0,
    #                   fill = (0, 0, 0, 100))
    # spectrum_ax.addItem(text)
    spectrum_ax.addLegend(offset=(200, 30))


def updateMotion():
    global transmot_ax, rotmot_ax, whichfile, alldata, namelist, win, numelements
    thisfile = alldata[namelist[whichfile]]
    windowtitle = "Grader - {0} ({1} of {2})".format(namelist[whichfile], whichfile, numelements)
    win.setWindowTitle(windowtitle)

    if thisfile["grade"] is None:
        pencolor = "w"
    elif thisfile["grade"] == 0:
        pencolor = "w"
    elif thisfile["grade"] > 0:
        pencolor = "g"
    else:
        pencolor = "r"

    timecourse_ax.plot(
        thisfile["timeaxis"],
        thisfile["timecourse"],
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=1),
        clear=True,
    )

    if thisfile["grade"] is None:
        thelabel = "Grade: None"
    else:
        thelabel = "Grade: {0}".format(thisfile["grade"])

    spectrum_ax.plot(
        thisfile["freqaxis"],
        thisfile["spectrum"],
        name=thelabel,
        stepMode=False,
        fillLevel=0,
        pen=pg.mkPen(pencolor, width=1),
        clear=True,
    )

    spectop = 1.25 * np.max(thisfile["spectrum"])
    spectrum_ax.setYRange(0.0, spectop, padding=0)

    # text = pg.TextItem(text=thelabel,
    #                   anchor = (0.0, 1.0),
    #                   angle = 0,
    #                   fill = (0, 0, 0, 100))
    # spectrum_ax.addItem(text)
    spectrum_ax.addLegend(offset=(200, 30))


def updateLightbox():
    global hist
    global currentdataset
    global maps
    global panetomap
    global ui
    global mainwin
    global currentloc
    global xdim, ydim, zdim
    global overlays
    global imagadj
    global whichfile

    mainwin.setTpos(whichfile)
    mainwin.updateAllViews()


def main():
    global ui, win
    global namelist, outputfile, alldata, whichfile, numelements
    global mainwin

    mainwin = None

    parser = argparse.ArgumentParser(
        description="A program to sort through timecourses and assign grades"
    )
    datasource = parser.add_mutually_exclusive_group()
    datasource.add_argument(
        "--filespec",
        type=str,
        help="A regex (with path) that will select files.  Should be enclosed in quotes.",
        default=None,
    )
    datasource.add_argument(
        "--reopen",
        type=lambda x: pica_util.is_valid_file(parser, x),
        help="Reopen a previously opened grader session output file.",
        default=None,
    )

    parser.add_argument("--outputfile", type=str, help="The name of the output file")

    sampling = parser.add_mutually_exclusive_group()
    sampling.add_argument(
        "--samplerate",
        dest="samplerate",
        action="store",
        metavar="FREQ",
        type=lambda x: pica_util.is_float(parser, x),
        help=(
            "Set the sample rate of the data file to FREQ. "
            "If neither samplerate or sampletime is specified, sample rate is 1.0."
        ),
        default="auto",
    )
    sampling.add_argument(
        "--sampletime",
        dest="samplerate",
        action="store",
        metavar="TSTEP",
        type=lambda x: pica_util.invert_float(parser, x),
        help=(
            "Set the sample rate of the data file to 1.0/TSTEP. "
            "If neither samplerate or sampletime is specified, sample rate is 1.0."
        ),
        default="auto",
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

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Use --help option for detailed information on options.")
        raise

    runmode = "aroma"
    args.aromaICfile = "/Users/frederic/Documents/MR_data/workdirs/Axial/fmriprep_wf/single_subject_005_wf/ica_aroma_wf/melodic/melodic_IC.nii.gz"
    args.aromaICmask = "/Users/frederic/Documents/MR_data/workdirs/Axial/fmriprep_wf/single_subject_005_wf/ica_aroma_wf/melodic/mask.nii.gz"
    args.aromaBGfile = "/usr/local/fsl/data/standard/MNI152_T1_2mm.nii.gz"
    args.aromaMotionfile = "/Users/frederic/Documents/MR_data/Axial/derivatives/fmriprep/sub-005/ses-001/func/sub-005_ses-001_run-2_task-rest_desc-confounds_regressors.json"
    args.aromaMix = "/Users/frederic/Documents/MR_data/workdirs/Axial/fmriprep_wf/single_subject_005_wf/ica_aroma_wf/melodic/melodic_mix"
    args.aromaPreclean = "/Users/frederic/Documents/MR_data/Axial/derivatives/fmriprep/sub-005/ses-001/func/sub-005_ses-001_task-rest_run-1_space-MNI152NLin6Asym_desc-preproc_bold.nii.gz"

    if (args.filespec is None) and (args.reopen is None):
        print("a data source must be specified")
        sys.exit()

    if args.outputfile is None:
        print("output file must be specified")
        sys.exit()

    # set the sample rate
    if args.samplerate == "auto":
        samplerate = 25.0
    else:
        samplerate = args.samplerate

    outputfile = args.outputfile
    if args.filespec is not None:
        namelist = glob.glob(args.filespec)
        if len(namelist) == 0:
            print("filespec returned no files")
            sys.exit()
        grades = None
        samplerates = None
    elif args.reopen is not None:
        df = pd.read_csv(args.reopen, header=None)
        namelist = df.iloc[:, 0].to_numpy()
        if len(namelist) == 0:
            print("reopen returned no files")
            sys.exit()
        grades = df.iloc[:, 1].to_numpy()
        samplerates = df.iloc[:, 2].to_numpy()
    else:
        print("either filespec or reopen must be specified")
        sys.exit()

    whichfile = 0

    print("reading data...")
    alldata = {}
    numelements = 0
    for idx in range(len(namelist)):
        thefile = namelist[idx]
        if grades is not None:
            thegrade = grades[idx]
        else:
            thegrade = 0
        if samplerates is not None:
            thesamplerate = samplerates[idx]
        else:
            thesamplerate = samplerate
        alldata[thefile] = {}
        invec = np.loadtxt(thefile)
        alldata[thefile]["timecourse"] = invec * 1.0
        alldata[thefile]["timeaxis"] = (
            np.linspace(0.0, 1.0 * (len(invec) - 1), num=len(invec), endpoint=True) / thesamplerate
        )
        alldata[thefile]["freqaxis"], alldata[thefile]["spectrum"] = spectrum(
            hamming(len(invec)) * invec, Fs=thesamplerate, mode="power"
        )
        alldata[thefile]["grade"] = thegrade
        alldata[thefile]["samplerate"] = thesamplerate
        print(thefile, thegrade, thesamplerate)

        numelements += 1
    print("Read in", numelements, "files")

    # make the main window
    if pyqtversion == 5:
        if runmode == "timecourse":
            import picachooser.graderTemplate as uiTemplate
        elif runmode == "aroma":
            import picachooser.aromaviewTemplate as uiTemplate
        else:
            print("illegal runmode")
            sys.exit()
    else:
        if runmode == "timecourse":
            import picachooser.graderTemplate_qt6 as uiTemplate
        elif runmode == "aroma":
            import picachooser.aromaviewTemplate_qt6 as uiTemplate
        else:
            print("illegal runmode")
            sys.exit()

    app = QtWidgets.QApplication([])
    print("setting up output window")
    win = KeyPressWindow()
    win.sigKeyPress.connect(keyPressed)
    win.sigResize.connect(windowResized)

    ui = uiTemplate.Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    win.setWindowTitle("Grader")

    # set up the regressor timecourse window
    print("about to set up the timecourse")
    global timecourse_ax
    timecoursewin = ui.timecourse_graphicsView
    timecourse_ax = timecoursewin.addPlot()

    # set up the regressor spectrum window
    print("about to set up the spectrum")
    global spectrum_ax
    spectrumwin = ui.spectrum_graphicsView
    spectrum_ax = spectrumwin.addPlot()

    global transmot_ax, rotmot_ax
    if runmode == "aromatic":
        # set up the translational motion window
        print("about to set up the translational motion")
        transmotwin = ui.translation_graphicsView
        transmot_ax = transmotwin.addPlot()

        # set up the translational motion window
        print("about to set up the translational motion")
        rotmotwin = ui.rotation_graphicsView
        rotmot_ax = rotmotwin.addPlot()
    elif runmode == "timecourse":
        transmot_ax = None
        rotmot_ax = None
    else:
        transmot_ax = None
        rotmot_ax = None

    updateTimecourse()

    if runmode == "aroma":
        thresh = 0.5
        print("setting up image window")
        maskimage = lb.imagedataset("ICmask", args.aromaICmask, "ICmask", lut_state=lb.mask_state)
        fgimage = lb.imagedataset(
            "IC",
            args.aromaICfile,
            "IC",
            lut_state=lb.ry_blb_state,
            geommask=maskimage.data,
        )
        funcmaskimage = fgimage.maskeddata * 1.0
        funcmaskimage[np.where(np.fabs(fgimage.data) < thresh)] = 0
        fgimage.setFuncMask(funcmaskimage)
        bgimage = lb.imagedataset("BG", args.aromaBGfile, "background", lut_state=lb.viridis_state)
        mainwin = lb.LightboxItem(fgimage, ui.image_graphicsView, bgmap=bgimage)
        updateLightbox()

    # wire up keystrokes to control interface

    QtWidgets.QApplication.instance().exec()


def entrypoint():
    main()


if __name__ == "__main__":
    entrypoint()
