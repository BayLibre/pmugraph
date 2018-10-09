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

from time import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QApplication, QWidget, QSplitter
from pyqtgraph import setConfigOption, PlotWidget
from pyqtgraph.parametertree import Parameter, ParameterTree
from regicepmu.perf import Perf

class PMUData:
    """
        A class to collect PMU data.

        This could be used by one or more graphs to display the data.
        :param event: The event to collect data from
    """
    def __init__(self, event, window_size):
        self.graphs = []
        self.data = [0] * window_size
        self.time = [0] * window_size
        self.event = event
        self.event.enable()
        self.tstart = time()

    def add_graph(self, graph):
        """
            Add a graph to update on event update.

            :param graph: The PMUGraph object that will display data
        """
        graph.init(self.event, self.time, self.data)
        self.graphs.append(graph)

    def update(self):
        """
            Get a performance event and update the graph
        """
        self.data.append(self.event.get_value())
        self.time.append(time() - self.tstart)
        for graph in self.graphs:
            graph.update(self.event, self.time, self.data)

class PMUGraph:
    """
        A class to display one or more performance graph,
        for the same performance event type

        :param pmuwidget: A PMUWidget object
        :param event_type: The type of performance event to display
    """
    def __init__(self, pmuwidget, event_type, window_size):
        self.plot = PlotWidget()
        self.perf = pmuwidget.perf
        self.parameters = pmuwidget.parameters
        self.window_size = window_size

        self.curves = {}
        self.events = self.perf.get_events(event_type)

        event_type_obj = self.perf.get_event_type(event_type)
        if event_type_obj.has_limits():
            y_min, y_max = event_type_obj.get_limits()
            self.plot.setYRange(y_min, y_max)
        self.plot.setLabel('left', event_type_obj.get_name(),
                           event_type_obj.get_unit())
        self.plot.setLabel('bottom', 'Time', 's')

        pmuwidget.vsplitter.addWidget(self.plot)
        pmuwidget.graphs.append(self)

    def init(self, event, data_time, data):
        """
            Initialize the graph

            :param event: The event to display
            :param data: The event's data
        """
        name = event.get_name()
        event_type_name = event.get_event_type().get_name()
        color = self.parameters.param(event_type_name, name, 'color').value()
        self.curves[name] = self.plot.plot(data_time, data)
        self.curves[name].setPen(color, width=3)

    def update(self, event, data_time, data):
        """
            Update the graph

            :param event: The event to display
            :param data: The event's data
        """
        name = event.get_name()
        if self.window_size is None:
            self.curves[name].setData(data_time, data)
        else:
            new_data_time = []
            dt0 = data_time[-self.window_size]
            for dt in data_time[-self.window_size:]:
                new_data_time.append(dt-dt0)
            self.curves[name].setData(new_data_time,
                                      data[-self.window_size:])

    def treeChanged(self):
        """
            Update graph option when a parameter has been changed

            This updates the color, and show or hide the graph
            when one of this option has been changed in the parameter
            tree.
        """
        for event in self.events:
            name = event.get_name()
            event_type_name = event.get_event_type().get_name()
            color = self.parameters.param(event_type_name, name, 'color').value()
            plot = self.parameters.param(event_type_name, name, 'plot').value()
            if plot:
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
    def __init__(self, perf, events_type, window_size):
        super(PMUWidget, self).__init__()
        self.perf = perf
        self.events_type = events_type
        self.window_size = window_size

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
        self.data = []

    def addEventGraph(self):
        """
            For each type of perf event, add a graph
        """
        setConfigOption('foreground', 'k')
        setConfigOption('background', 'w')
        for event_type in self.events_type:
            graph_window = PMUGraph(self, event_type, self.window_size)
            for event in self.perf.get_events(event_type):
                data = PMUData(event, self.window_size)
                data.add_graph(graph_window)
                self.data.append(data)

        self.hsplitter.addWidget(self.vsplitter)

    def addEventParameterTree(self, event_type):
        """
            For each perf event, add a parameter to parameter tree.
        """
        children = []
        color = iter(self.colors)
        events = self.perf.get_events(event_type)
        for event in events:
            event_group = {
                'type': 'group',
                'name': event.get_name(),
                'children' : [
                    { 'type': 'bool', 'name': 'plot', 'value': True },
                    { 'type': 'color', 'name': 'color', 'value': next(color) },
                ]
            }
            children.append(event_group)
        return children

    def addEventTypeParameterTree(self):
        """
            For each perf event, add a parameter to parameter tree.
        """
        children = []
        for event_type in self.events_type:
            event_type_obj = self.perf.get_event_type(event_type)
            event_type_group = {
                'type': 'group',
                'name': event_type_obj.get_name(),
                'children': self.addEventParameterTree(event_type)
            }
            children.append(event_type_group)

        self.parameters = Parameter.create(name='params', type='group',
                                           children=children)
        self.parameters.sigTreeStateChanged.connect(self.treeChanged)
        self.tree.setParameters(self.parameters, showTop=False)
        self.hsplitter.addWidget(self.tree)

    def update(self):
        """
            Update the graphs
        """
        for data in self.data:
            data.update()

    def treeChanged(self):
        """
            Called when a value have changed
        """
        for graph in self.graphs:
            graph.treeChanged()
