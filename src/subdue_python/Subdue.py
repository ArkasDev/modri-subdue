# Subdue.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017-2021. Washington State University.

import sys
import time
import json
import contextlib
import subdue_python.Graph as Graph
import subdue_python.Pattern as Pattern
import subdue_python.Parameters as Parameters
import os
import json
from random import randrange
import experiment_scripts.compute_components
from experiment_scripts.algorithms import is_subgraph_mono, is_label_isomorphic
from experiment_scripts.compute_components import load_components_networkx
from termcolor import colored
from experiment_scripts.evaluation import plot_graphs

DEBUGFLAG = False


def main():
    parameters = Parameters.Parameters()
    parameters.set_parameters(sys.argv)

    # Read graph and save it in the graph data structure
    graph = read_graph(parameters.inputFileName)

    parameters.set_defaults_for_graph(graph)

    if not parameters.beamSearchDebugging:
        parameters.print()

    # Execute subdue_python algorithm
    subdue(parameters, graph)


def read_graph(input_file_name):
    """
    Read graph from given filename.
    """

    # Load graph from file
    with open(input_file_name, 'r') as input_graph_file:
        json_graph = json.load(input_graph_file)

        # Create graph data structure
        graph = Graph.Graph()
        graph.load_from_json(json_graph)

        return graph


def subdue(parameters, graph):
    """
    Top-level function for Subdue that discovers best pattern in graph.
    Optionally, Subdue can then compress the graph with the best pattern, and iterate.

    :param graph: instance of Subdue.Graph
    :param parameters: instance of Subdue.Parameters
    :return: patterns for each iteration -- a list of iterations each containing discovered patterns.
    """

    iteration = 1
    done = False

    # Store found pattern as list
    patterns = list()

    # Iterate
    while (iteration <= parameters.iterations) and (not done):

        # Start with the performance test for this single iteration
        iteration_start_time = time.time()

        # Show pretty output for this iteration with input graph information
        if iteration > 1:
            print("----- Iteration " + str(iteration) + " -----\n")

        if not parameters.beamSearchDebugging:
            print("Graph: " + str(len(graph.vertices)) + " vertices, " + str(len(graph.edges)) + " edges")

        # 1. PHASE: Start with substructure discovery
        # Temporary list of found patterns in this iteration
        pattern_list = substructure_discover(parameters, graph)

        if (not pattern_list):
            done = True
            print("No patterns found.\n")
        else:
            patterns.append(pattern_list)
            if not parameters.beamSearchDebugging:
                print("\nBest " + str(len(pattern_list)) + " patterns:\n")
                for pattern in pattern_list:
                    pattern.print_pattern('  ')
                    print("")
            # write machine-readable output, if requested
            if (parameters.writePattern):
                outputFileName = parameters.outputFileName + "-pattern-" + str(iteration) + ".json"
                pattern_list[0].definition.write_to_file(outputFileName)
            if (parameters.writeInstances):
                outputFileName = parameters.outputFileName + "-instances-" + str(iteration) + ".json"
                pattern_list[0].write_instances_to_file(outputFileName, parameters.experimentFolder)
            if ((iteration < parameters.iterations) or (parameters.writeCompressed)):
                graph.Compress(iteration, pattern_list[0])
            if (iteration < parameters.iterations):
                # consider another iteration
                if (len(graph.edges) == 0):
                    done = True
                    print("Ending iterations - graph fully compressed.\n")
            if ((iteration == parameters.iterations) and (parameters.writeCompressed)):
                outputFileName = parameters.outputFileName + "-compressed-" + str(iteration) + ".json"
                graph.write_to_file(outputFileName)
        if (parameters.iterations > 1):
             iterationEndTime = time.time()
             print("Elapsed time for iteration " + str(iteration) + " = " + str(iterationEndTime - iteration_start_time) + " seconds.\n")
        iteration += 1

    return patterns


def substructure_discover(parameters, graph):
    """
    The main discovery loop. Finds and returns best patterns in given graph.

    :param graph: Instance of Subdue.Graph
    :param parameters: Instance of Subdue.Parameters
    :return: Best patterns in the given graph for the current iteration
    """

    # How many times the root loop was run
    root_count = 0

    # How many patterns found in the graph
    pattern_count = 0

    # Get initial one-edge patterns
    parent_pattern_list = get_initial_patterns(parameters, graph)

    if parameters.beamSearchDebugging:
        print("-----------------------------")
        print("initial pattern: " + str(len(parent_pattern_list)))

    if parameters.beamSearchDebugging:
        step = "1. init"
        for pattern in parent_pattern_list:
            value = "%.4f" % pattern.value
            path = parameters.experimentFolder + "/beam_search/" + step + "/"
            name = "c_" + str(value) + \
                   "__i_" + str(len(pattern.instances)) + \
                   "__" + str(randrange(1000))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pattern.write_pattern_to_file(path + name + ".json")
            pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(path + name + ".json")
            plot_graphs([pattern_nx], path + name)

    if parameters.beamSearchDebugging:
        for parent in parent_pattern_list:
            print("compression of pattern: " + str(parent.value))

    discoveredPatternList = []

    while ((pattern_count < parameters.limit) and parent_pattern_list):

        # Only for debugging purposes
        root_count += 1

        if parameters.beamSearchDebugging:
            if pattern_count > 0:
                print(colored("Deleting child patterns...", "yellow"))

        childPatternList = []

        # iterate parent patterns
        while (parent_pattern_list):

            if parameters.beamSearchDebugging:
                print(colored("-----------------------------", "green"))
                print(colored("Start a parent pattern loop", "green"))
                print("limit: " + str(pattern_count))
                print("parent patterns: " + str(len(parent_pattern_list)))

            parentPattern = parent_pattern_list.pop(0)
            if ((len(parentPattern.instances) > 1) and (pattern_count < parameters.limit)):
                pattern_count += 1

                if parameters.beamSearchDebugging:
                    print("start expansion...")

                extendedPatternList = Pattern.ExtendPattern(parameters, parentPattern)

                if parameters.beamSearchDebugging:
                    step = "2. expansion"
                    for pattern in extendedPatternList:
                        path = parameters.experimentFolder + "/beam_search/" + step + "/" + str(root_count) + "_" + str(pattern_count) + "/"
                        name = "i_" + str(len(pattern.instances)) + \
                               "__" + str(randrange(1000))
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        pattern.write_pattern_to_file(path + name + ".json")
                        pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
                            path + name + ".json")
                        plot_graphs([pattern_nx], path + name)

                if parameters.beamSearchDebugging:
                    print("expanded patterns: " + str(len(extendedPatternList)))

                while (extendedPatternList):
                    extendedPattern = extendedPatternList.pop(0)

                    # only evaluate compression if #edges is lower then the defined max size
                    if (len(extendedPattern.definition.edges) <= parameters.maxSize):

                        # evaluate the compression of each extension
                        extendedPattern.evaluate(graph)

                        if parameters.beamSearchDebugging:
                            print("compression before: " + str(parentPattern.value) + ", after: " + str(extendedPattern.value))

                        # prune = false --> add pattern to child patterns
                        # prune = true --> add pattern to child patterns only if the extended pattern has higher compression
                        # child pattern are used for the next expansion
                        if ((not parameters.prune) or (extendedPattern.value >= parentPattern.value)):
                            Pattern.PatternListInsert(extendedPattern, childPatternList, parameters.beamWidth, parameters.valueBased)
                            if parameters.beamSearchDebugging:
                                print(colored("Add extended pattern to child patterns", "grey"))
                        else:
                            if parameters.beamSearchDebugging:
                                print(colored("Too bad compression. Do not add extended pattern to child patterns", "grey"))
            else:
                if parameters.beamSearchDebugging:
                    print("Limit reached, no expansion anymore")

            # add parent pattern to final discovered list
            if (len(parentPattern.definition.edges) >= parameters.minSize):
                Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False)
                if parameters.beamSearchDebugging:
                    print("Add the parent pattern to the final patterns")
            else:
                if parameters.beamSearchDebugging:
                    print(colored("Pattern to small. Its not a good pattern", "red"))

            if parameters.beamSearchDebugging:
                step = "3. current"
                for pattern in discoveredPatternList:
                    value = "%.4f" % pattern.value
                    path = parameters.experimentFolder + "/beam_search/" + step + "/discovered/" + str(root_count) + "_" + str(pattern_count) + "/"
                    name = "c_" + str(value) + \
                           "__i_" + str(len(pattern.instances)) + \
                           "__" + str(randrange(1000))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    pattern.write_pattern_to_file(path + name + ".json")
                    pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(path + name + ".json")
                    plot_graphs([pattern_nx], path + name)
                for pattern in childPatternList:
                    value = "%.4f" % pattern.value
                    path = parameters.experimentFolder + "/beam_search/" + step + "/child/" + str(root_count) + "_" + str(pattern_count) + "/"
                    name = "c_" + str(value) + \
                           "__i_" + str(len(pattern.instances)) + \
                           "__" + str(randrange(1000))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    pattern.write_pattern_to_file(path + name + ".json")
                    pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(path + name + ".json")
                    plot_graphs([pattern_nx], path + name)
                for pattern in parent_pattern_list:
                    value = "%.4f" % pattern.value
                    path = parameters.experimentFolder + "/beam_search/" + step + "/parent/" + str(root_count) + "_" + str(pattern_count) + "/"
                    name = "c_" + str(value) + \
                           "__i_" + str(len(pattern.instances)) + \
                           "__" + str(randrange(1000))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    pattern.write_pattern_to_file(path + name + ".json")
                    pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(path + name + ".json")
                    plot_graphs([pattern_nx], path + name)

            if parameters.beamSearchDebugging:
                print(colored("discovered patterns: " + str(len(discoveredPatternList)), "blue"))
                print(colored("parent patterns: " + str(len(parent_pattern_list)), "blue"))
                print(colored("child patterns: " + str(len(childPatternList)), "blue"))

        if parameters.beamSearchDebugging:
            print(colored("Parent pattern loop finished", "magenta"))

        parent_pattern_list = childPatternList

    if parameters.beamSearchDebugging:
        print(colored("Insert any remaining patterns in parent list on to discovered list", "magenta"))
        print(colored("parent_pattern_list: " + str(len(parent_pattern_list)),  "magenta"))

    # insert any remaining patterns in parent list on to discovered list
    while (parent_pattern_list):
        parentPattern = parent_pattern_list.pop(0)
        if (len(parentPattern.definition.edges) >= parameters.minSize):
            Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False)

    if parameters.beamSearchDebugging:
        print(colored("discoveredPatternList: " + str(len(discoveredPatternList)), "blue"))

    if parameters.beamSearchDebugging:
        step = "4. result"
        for pattern in discoveredPatternList:
            value = "%.4f" % pattern.value
            path = parameters.experimentFolder + "/beam_search/" + step + "/"
            name = "c_" + str(value) + \
                   "__i_" + str(len(pattern.instances)) + \
                   "__" + str(randrange(1000))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pattern.write_pattern_to_file(path + name + ".json")
            pattern_nx = experiment_scripts.compute_components.convert_node_link_graph_to_nx_graph(
                path + name + ".json")
            plot_graphs([pattern_nx], path + name)

    return discoveredPatternList


def get_initial_patterns(parameters, graph):
    """
    Returns list of single-edge, evaluated patterns in given graph with more than one instance.
    """
    # Save all found single-edge patterns in the current graph
    initial_patterns = []

    # Create a graph and an instance for each edge
    edge_graph_instance_pairs = []

    #
    for edge in graph.edges.values():
        graph = Graph.CreateGraphFromEdge(edge)

        if parameters.temporal:
            graph.TemporalOrder()

        instance1 = Pattern.CreateInstanceFromEdge(edge)
        edge_graph_instance_pairs.append((graph,instance1))

    while edge_graph_instance_pairs:
        edgePair1 = edge_graph_instance_pairs.pop(0)
        graph = edgePair1[0]
        instance1 = edgePair1[1]
        pattern = Pattern.Pattern()
        pattern.definition = graph
        pattern.instances.append(instance1)
        nonmatchingEdgePairs = []
        for edgePair2 in edge_graph_instance_pairs:
            graph2 = edgePair2[0]
            instance2 = edgePair2[1]
            if Graph.GraphMatch(graph, graph2) and (not Pattern.InstancesOverlap(parameters.overlap, pattern.instances, instance2)):
                pattern.instances.append(instance2)
            else:
                nonmatchingEdgePairs.append(edgePair2)
        if len(pattern.instances) > 1:
            pattern.evaluate(graph)
            initial_patterns.append(pattern)
        edge_graph_instance_pairs = nonmatchingEdgePairs
    return initial_patterns



def nx_subdue(
    graph,
    node_attributes=None,
    edge_attributes=None,
    verbose=False,
    **subdue_parameters
):
    """
    :param graph: networkx.Graph
    :param node_attributes: (Default: None)   -- attributes on the nodes to use for pattern matching, use `None` for all
    :param edge_attributes: (Default: None)   -- attributes on the edges to use for pattern matching, use `None` for all
    :param verbose: (Default: False)          -- if True, print progress, as well as report each found pattern

    :param beamWidth: (Default: 4)            -- Number of patterns to retain after each expansion of previous patterns; based on value.
    :param iterations: (Default: 1)           -- Iterations of Subdue's discovery process. If more than 1, Subdue compresses graph with best pattern before next run. If 0, then run until no more compression (i.e., set to |E|).
    :param limit: (Default: 0)                -- Number of patterns considered; default (0) is |E|/2.
    :param maxSize: (Default: 0)              -- Maximum size (#edges) of a pattern; default (0) is |E|/2.
    :param minSize: (Default: 1)              -- Minimum size (#edges) of a pattern; default is 1.
    :param numBest: (Default: 3)              -- Number of best patterns to report at end; default is 3.
    :param overlap: (Defaul: none)            -- Extent that pattern instances can overlap (none, vertex, edge)
    :param prune: (Default: False)            -- Remove any patterns that are worse than their parent.
    :param valueBased: (Default: False)       -- Retain all patterns with the top beam best values.
    :param temporal: (Default: False)         -- Discover static (False) or temporal (True) patterns

    :return: list of patterns, where each pattern is a list of pattern instances, with an instance being a dictionary
    containing 
        `nodes` -- list of IDs, which can be used with `networkx.Graph.subgraph()`
        `edges` -- list of tuples (id_from, id_to), which can be used with `networkx.Graph.edge_subgraph()`
    
    For `iterations`>1 the the list is split by iterations, and some patterns will contain node IDs not present in
    the original graph, e.g. `PATTERN-X-Y`, such node ID refers to a previously compressed pattern, and it can be 
    accessed as `output[X-1][0][Y]`.

    """
    parameters = Parameters.Parameters()
    if len(subdue_parameters) > 0:
        parameters.set_parameters_from_kwargs(**subdue_parameters)
    subdue_graph = Graph.Graph()
    subdue_graph.load_from_networkx(graph, node_attributes, edge_attributes)
    parameters.set_defaults_for_graph(subdue_graph)
    if not parameters.beamSearchDebugging:
        parameters.print()
    if verbose:
        iterations = subdue(parameters, subdue_graph)
    else:
        with contextlib.redirect_stdout(None):
            iterations = subdue(parameters, subdue_graph)
    iterations = unwrap_output(iterations)
    if parameters.iterations == 1:
        if len(iterations) == 0:
            return None
        return iterations[0]
    else:
        return iterations

def unwrap_output(iterations):
    """
    Subroutine of `nx_Subdue` -- unwraps the standard Subdue output into pure python objects compatible with networkx
    """
    out = list()
    for iteration in iterations:
        iter_out = list()
        for pattern in iteration:
            pattern_out = list()
            for instance in pattern.instances:
                pattern_out.append({
                    'nodes': [vertex.id for vertex in instance.vertices],
                    'edges': [(edge.source.id, edge.target.id) for edge in instance.edges]
                })
            iter_out.append(pattern_out)
        out.append(iter_out)
    return out


if __name__ == "__main__":
    main()
