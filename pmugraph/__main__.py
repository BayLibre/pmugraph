#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from regicecommon.helpers import init_argument_parser, process_arguments
from regicepmu.perf import Perf

from pmugraph.pmugraph import PMUWidget

def main():
    plugins = ['regicepmu']
    parser = init_argument_parser(plugins)
    parser.add_argument('--cpu-load', action='store_true',
                        help='Display the cpu load')
    parser.add_argument('--memory-load', action='store_true',
                        help='Display the memory load')
    results = process_arguments(parser, plugins)
    device = results[0]
    perf = Perf(device)

    parser = init_argument_parser(plugins, device)
    results = process_arguments(parser, plugins, device)
    args = results[1]

    sample_rate = 10
    time_size = 10

    app = QApplication(sys.argv)

    if not args.events:
        print('A least one perf event have to be selected.')
        sys.exit(1)

    win = PMUWidget(perf, args.events, sample_rate * time_size)
    win.addEventTypeParameterTree()
    win.addEventGraph()
    win.setWindowTitle('PMUGraph')
    win.show()

    timer = QTimer()
    timer.timeout.connect(win.update)
    timer.start(1000 / sample_rate)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()

if __name__ == "__main__":
    main()
