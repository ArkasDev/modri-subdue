# Pattern.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017-2021. Washington State University.
from termcolor import colored

from src.subdue_python.OrderedSet import OrderedSet # specialized Subdue version
import src.subdue_python.Graph as Graph
import uuid
import sys
import os
import json
from random import randrange
import copy


class Pattern:
    
    def __init__(self):
        self.definition = None # Graph
        self.instances = []
        self.value = 0.0

    def evaluate(self, graph_input, eval, overlap):
        if eval == 1:
            self.evaluate_compression_via_heuristic(graph_input)
        if eval == 2:
            self.evaluate_compression_via_size(graph_input, overlap)
        if eval == 3:
            self.evaluate_compression_via_size_wo_preserved(graph_input, overlap)
        if eval == 4:
            self.value = float(len(self.instances) - 1) * (len(self.definition.edges) + len(self.definition.vertices))

    def calc_size_wo_preserve_for_edges(self, graph):
        e = len(graph.edges)
        for edge_id in graph.edges:
            if "Preserve" in graph.edges[edge_id].attributes['label']:
                e = e - 1
        return e

    def calc_size_wo_preserve_for_vertices(self, graph):
        v = len(graph.vertices)
        for v_id in graph.vertices:
            if "Preserve" in graph.vertices[v_id].attributes['label']:
                v = v - 1
        return v

    def evaluate_compression_via_heuristic(self, graph_input):
        """Compute value of using given pattern to compress given graph, where 0 means no compression, and 1 means perfect compression."""
        # (instances-1) because we would also need to retain the definition of the pattern for compression
        self.value = float(((len(self.instances) - 1) * len(self.definition.edges)) / float(len(graph_input.edges)))

    def evaluate_compression_via_size(self, graph_input, overlap):
        size_of_compressed_graph = self.calc_size_of_compressed_graph(graph_input, overlap)
        self.value = float(self.calc_size(graph_input)) / float(self.calc_size(self.definition) + size_of_compressed_graph)

    # TODO: add overlapping
    def calc_size_of_compressed_graph(self, graph, overlap):
        size = self.calc_size(graph)
        for instance in self.instances:
            size = size + 1
            size_of_instance = len(instance.vertices.list_container) + len(instance.edges.list_container)
            size = size - size_of_instance
        return size

    def calc_size(self, graph):
        size = len(graph.vertices) + len(graph.edges)
        return size

    # def evaluate_compression_via_size_wo_preserved(self, graph_input, overlap):
    #     size_of_compressed_graph = self.calc_size_of_compressed_graph_wo_preserved(graph_input, overlap)
    #     self.value = float(self.calc_size_wo_preserved(graph_input)) / float(self.calc_size_wo_preserved(self.definition) + size_of_compressed_graph)

    def evaluate_compression_via_size_wo_preserved(self, graph_input, overlap):
        size_of_compressed_graph = self.calc_size_of_compressed_graph(graph_input, overlap)
        self.value = float(self.calc_size(graph_input)) / float(self.calc_size_wo_preserved(self.definition) + size_of_compressed_graph)

    # TODO: add overlapping
    def calc_size_of_compressed_graph_wo_preserved(self, graph, overlap):
        size = self.calc_size_wo_preserved(graph)
        for instance in self.instances:
            size = size + 1

            e = len(instance.edges.list_container)
            for edge_id in instance.edges.list_container:
                if "Preserve" in edge_id.attributes['label']:
                    e = e - 1
            v = len(instance.vertices.list_container)
            for v_id in instance.vertices.list_container:
                if "Preserve" in v_id.attributes['label']:
                    v = v - 1

            size = size - (v + e)
        return size

    def calc_size_wo_preserved(self, graph):
        e = len(graph.edges)
        for edge_id in graph.edges:
            if "Preserve" in graph.edges[edge_id].attributes['label']:
                e = e - 1
        v = len(graph.vertices)
        for v_id in graph.vertices:
            if "Preserve" in graph.vertices[v_id].attributes['label']:
                v = v - 1

        size = v + e
        return size

    def calc_overlap_edges(self):
        num_overlap_edges = 0

        instances_list = self.instances

        while instances_list:
            current_instance = instances_list.pop()
            # check other instances
            for instance in instances_list:
                # loop for every current instance edge...
                for current_instance_edge in current_instance.edges.list_container:
                    # over all edges in the other instance
                    for instance_edge in instance.edges.list_container:
                        if current_instance_edge.id == instance_edge.id:
                            num_overlap_edges = num_overlap_edges + 1

        return num_overlap_edges

    def print_pattern(self, tab):
        print(tab + "Pattern (value=" + str(self.value) + ", instances=" + str(len(self.instances)) + "):")
        self.definition.print_graph(tab+'  ')
        # May want to make instance printing optional
        instanceNum = 1
        for instance in self.instances:
            instance.print_instance(instanceNum, tab+'  ')
            instanceNum += 1

    def write_pattern_to_file(self, outputFileName):
        outputFile = open(outputFileName, 'w')
        outputFile.write('[\n')
        for instance in self.instances:
            instance.write_to_file(outputFile)
            break
        outputFile.write('\n]\n')
        outputFile.close()

    def write_instances_to_file(self, outputFileName, outputDir=""):
        """Write instances of pattern to given file name in JSON format."""
        outputFile = open(outputFileName, 'w')
        outputFile.write('[\n')
        firstOne = True
        instancesCounter = 0
        for instance in self.instances:
            instancesCounter = instancesCounter + 1
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            instance.write_to_file(outputFile)
        outputFile.write('\n]\n')
        outputFile.close()

        if outputDir != "":
            with open(outputDir + "/subdue_python_count_instances.txt", 'w') as instances_file:
                instances_file.write("# Pattern 1 \n")
                instances_file.write(str(instancesCounter) + "\n")

class Instance:
    
    def __init__(self):
        self.vertices = OrderedSet()
        self.edges = OrderedSet()
    
    def print_instance (self, instanceNum, tab=""):
        print(tab + "Instance " + str(instanceNum) + ":")
        for vertex in self.vertices:
            vertex.print_vertex(tab+'  ')
        for edge in self.edges:
            edge.print_edge(tab+'  ')
            
    def write_to_file(self, outputFile):
        """Write instance to given file stream in JSON format."""
        firstOne = True
        for vertex in self.vertices:
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            vertex.write_to_file(outputFile)
        outputFile.write(',\n')
        firstOne = True
        for edge in self.edges:
            if firstOne:
                firstOne = False
            else:
                outputFile.write(',\n')
            edge.write_to_file(outputFile)
    
    def max_timestamp(self):
        """Returns the maximum timestamp over all vertices and edges in the instance."""
        maxTimeStampVertex = max(self.vertices, key = lambda v: v.timestamp)
        maxTimeStampEdge = max(self.edges, key = lambda e: e.timestamp)
        return max(maxTimeStampVertex.timestamp, maxTimeStampEdge.timestamp)
        

# ----- Pattern and Instance Creation

def CreateInstanceFromEdge(edge):
    i = Instance()
    i.edges.add(edge)
    i.vertices.add(edge.source)
    i.vertices.add(edge.target)
    return i

def CreatePatternFromInstances(definition, instances):
    """Create pattern from given definition graph and its instances. Note: Pattern not evaluated here."""
    pattern = Pattern()
    pattern.definition = definition
    pattern.instances = instances
    return pattern

# ----- Pattern Extension

def ExtendPattern (parameters, pattern):
    """Return list of patterns created by extending each instance of the given pattern by one edge in all possible ways,
       and then collecting matching extended instances together into new patterns."""
    extendedInstances = []

    # Expansion
    for instance in pattern.instances:
        newInstances = ExtendInstance(instance)
        for newInstance in newInstances:
            InsertNewInstance(extendedInstances, newInstance)
    newPatterns = []

    # Check
    while extendedInstances:
        newInstance = extendedInstances.pop(0)
        newInstanceGraph = Graph.CreateGraphFromInstance(newInstance)
        if parameters.temporal:
            newInstanceGraph.TemporalOrder()
        matchingInstances = [newInstance]
        nonmatchingInstances = []
        for extendedInstance in extendedInstances:
            extendedInstanceGraph = Graph.CreateGraphFromInstance(extendedInstance)
            if parameters.temporal:
                extendedInstanceGraph.TemporalOrder()
            if Graph.GraphMatch(newInstanceGraph, extendedInstanceGraph) and (not InstancesOverlap(parameters.overlap, matchingInstances, extendedInstance)):
                matchingInstances.append(extendedInstance)
            else:
                nonmatchingInstances.append(extendedInstance)
        extendedInstances = nonmatchingInstances
        newPattern = CreatePatternFromInstances(newInstanceGraph, matchingInstances)
        newPatterns.append(newPattern)
    return newPatterns

def ExtendInstance (instance):
    """Returns list of new instances created by extending the given instance by one new edge in all possible ways."""
    newInstances = []
    unusedEdges = OrderedSet([e for v in instance.vertices for e in v.edges]) - instance.edges
    for edge in unusedEdges:
        newInstance = ExtendInstanceByEdge(instance, edge)
        newInstances.append(newInstance)
    return newInstances

def ExtendInstanceByEdge(instance, edge):
    """Create and return new instance built from given instance and adding given edge and vertices of edge if new."""
    newInstance = Instance()
    newInstance.vertices = OrderedSet(instance.vertices)
    newInstance.edges = OrderedSet(instance.edges)
    newInstance.edges.add(edge)
    newInstance.vertices.add(edge.source)
    newInstance.vertices.add(edge.target)
    return newInstance

def InsertNewInstance(instanceList, newInstance):
    """Add newInstance to instanceList if it does not match an instance already on the list."""
    match = False
    for instance in instanceList:
        if (InstanceMatch(instance,newInstance)):
            match = True
            break
    if not match:
        instanceList.append(newInstance)

def InstanceMatch(instance1,instance2):
    """Return True if given instances match, i.e., contain the same vertex and edge object instances."""
    if (instance1.vertices == instance2.vertices) and (instance1.edges == instance2.edges):
        return True
    else:
        return False

def InstancesOverlap(overlap, instanceList, instance):
    """Returns True if instance overlaps with an instance in the given instanceList
    according to the overlap parameter, which indicates what type of overlap ignored.
    Overlap="none" means no overlap ignored. Overlap="vertex" means vertex overlap
    ignored. Overlap="edge" means vertex and edge overlap ignored, but the instances
    cannot be identical."""
    for instance2 in instanceList:
        if InstanceOverlap(overlap, instance, instance2):
            return True
    return False

def InstanceOverlap(overlap, instance1, instance2):
    """Returns True if given instances overlap according to given overlap parameter.
    See InstancesOverlap for explanation."""
    if overlap == "edge":
        return InstanceMatch(instance1, instance2)
    elif overlap == "vertex":
        return instance1.edges.intersect(instance2.edges)
    else: # overlap == "none"
        return instance1.vertices.intersect(instance2.vertices)


# ----- Pattern List Operations

def PatternListInsert(newPattern, patternList, maxLength, valueBased, beamSearchDebugging=False, experimentFolder=None, limitCount=None):
    """Insert newPattern into patternList. If newPattern is isomorphic to an existing pattern on patternList, then keep higher-valued
       pattern. The list is kept in decreasing order by pattern value. If valueBased=True, then maxLength represents the maximum number
       of different-valued patterns on the list; otherwise, maxLength represents the maximum number of patterns on the list.
       Assumes given patternList already conforms to maximums."""
    # Check if newPattern unique (i.e., non-isomorphic or isomorphic but better-valued)
    for pattern in patternList:
        if (Graph.GraphMatch(pattern.definition, newPattern.definition)):
            if (pattern.value >= newPattern.value):
                return # newPattern already on list with same or better value
            else:
                # newpattern isomorphic to existing pattern, but better valued
                patternList.remove(pattern)
                break

    # pattern list before

    # newPattern unique, so insert in order by value
    insertAtIndex = 0
    for pattern in patternList:
        if newPattern.value > pattern.value:
            break
        insertAtIndex += 1
    patternList.insert(insertAtIndex, newPattern)

    # pattern list with new pattern

    # check if patternList needs to be trimmed
    if valueBased:
        uniqueValues = UniqueValues(patternList)
        if len(uniqueValues) > maxLength:
            removeValue = uniqueValues[-1]
            while (patternList[-1].value == removeValue):
                patternList.pop(-1)
    else:
        if len(patternList) > maxLength:
            patternList.pop(-1)

    # pattern list with new pattern trimmed based on beam width


def UniqueValues(patternList):
    """Returns list of unique values of patterns in given pattern list, in same order."""
    uniqueValues = []
    for pattern in patternList:
        if pattern.value not in uniqueValues:
            uniqueValues.append(pattern.value)
    return uniqueValues
