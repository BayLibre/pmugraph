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

import numpy

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QApplication, QWidget, QSplitter
from pyqtgraph import setConfigOption, PlotWidget
from pyqtgraph.parametertree import Parameter, ParameterTree
from regicepmu.perf import Perf

class PMUGraph:
    """
        A class to display one or more performance graph,
        for the same performance event type

        :param pmuwidget: A PMUWidget object
        :param event_type: The type of performance event to display
    """
    def __init__(self, pmuwidget, event_type):
        self.plot = PlotWidget()
        self.perf = pmuwidget.perf
        self.parameters = pmuwidget.parameters

        self.datas = {}
        self.curves = {}
        self.events = self.perf.get_events(event_type)

        if self.events[0].has_range():
            y_min, y_max = self.events[0].get_range()
            self.plot.setYRange(y_min, y_max)
        self.plot.setLabel('left', self.events[0].get_name(),
                           self.events[0].get_unit())
        self.plot.setLabel('bottom', 'Time', 's')

        for event in self.events:
            name = event.get_name()
            color = self.parameters.param(name, 'color').value()
            self.datas[name] = numpy.zeros(10)
            self.curves[name] = self.plot.plot(self.datas[name])
            self.curves[name].setPen(color, width=3)
            event.enable()

        pmuwidget.vsplitter.addWidget(self.plot)
        pmuwidget.graphs.append(self)

    def update(self):
        """
            Get a performance event and update the graph
        """
        for event in self.events:
            name = event.get_name()
            self.datas[name][:-1] = self.datas[name][1:]
            self.datas[name][-1] = event.get_value()
            self.curves[name].setData(self.datas[name])

    def treeChanged(self):
        """
            Update graph option when a parameter has been changed

            This updates the color, and show or hide the graph
            when one of this option has been changed in the parameter
            tree.
        """
        for event in self.events:
            plot = self.parameters.param(event.name, 'plot').value()
            if plot:
                color = self.parameters.param(event.name, 'color').value()
                self.curves[event.name].setPen(color, width=3)
                self.curves[event.name].show()
            else:
                self.curves[event.name].hide()

class PMUWidget(QWidget):
    """
        A widget to display the parameter tree and the graphs

        :param perf: A Perf object
        :param events_type: A list of perf event type to display
    """
    def __init__(self, perf, events_type):
        super(PMUWidget, self).__init__()
        self.perf = perf
        self.events_type = events_type

        self.tree = ParameterTree(showHeader=False)
        self.parameters = None
        self.colors = [
            "#0088FF", "#FF5500", "#449900", "#AA00AA",
            "#4444FF", "#994400", "#99AA00", "#990000",
        ]

        self.vsplitter = QSplitter(Qt.Vertical)
        self.hsplitter = QSplitter(Qt.Horizontal)
        box = QHBoxLayout(self)
        box.addWidget(self.hsplitter)

        self.graphs = []

    def addEventGraph(self):
        """
            For each type of perf event, add a graph
        """
        setConfigOption('foreground', 'k')
        setConfigOption('background', 'w')
        for event_type in self.events_type:
            PMUGraph(self, event_type)
        self.hsplitter.addWidget(self.vsplitter)

    def addEventParameterTree(self):
        """
            For each perf event, add a parameter to parameter tree.
        """
        children = []
        color = iter(self.colors)
        for event_type in self.events_type:
            events = self.perf.get_events(event_type)
            for event in events:
                children.append(dict(name=event.get_name(), type='group', children=[
                    dict(name='plot', type='bool', value=True),
                    dict(name='color', type='color', value=next(color))
                ]))
        self.parameters = Parameter.create(name='params', type='group',
                                           children=children)
        self.parameters.sigTreeStateChanged.connect(self.treeChanged)
        self.tree.setParameters(self.parameters, showTop=False)
        self.hsplitter.addWidget(self.tree)

    def update(self):
        """
            Update the graphs
        """
        for graph in self.graphs:
            graph.update()

    def treeChanged(self):
        """
            Called when a value have changed
        """
        for graph in self.graphs:
            graph.treeChanged()
