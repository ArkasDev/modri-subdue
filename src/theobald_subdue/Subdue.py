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

DEBUGFLAG = False


def main():
    parameters = Parameters.Parameters()
    parameters.set_parameters(sys.argv)

    # Read graph and save it in the graph data structure
    graph = read_graph(parameters.inputFileName)

    parameters.set_defaults_for_graph(graph)
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
        print("Graph: " + str(len(graph.vertices)) + " vertices, " + str(len(graph.edges)) + " edges")

        # 1. PHASE: Start with substructure discovery
        # Temporary list of found patterns in this iteration
        pattern_list = substructure_discover(parameters, graph)

        if (not pattern_list):
            done = True
            print("No patterns found.\n")
        else:
            patterns.append(pattern_list)
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
                pattern_list[0].write_instances_to_file(outputFileName)
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

    # How many patterns found in the graph
    pattern_count = 0

    # Get initial one-edge patterns
    parent_pattern_list = get_initial_patterns(parameters, graph)

    if DEBUGFLAG:
        print("Initial patterns (" + str(len(parent_pattern_list)) + "):")
        for pattern in parent_pattern_list:
            pattern.print_pattern('  ')

    discoveredPatternList = []
    while ((pattern_count < parameters.limit) and parent_pattern_list):
        print(str(int(parameters.limit - pattern_count)) + " ", flush=True)
        childPatternList = []
        # extend each pattern in parent list (***** todo: in parallel)
        while (parent_pattern_list):
            parentPattern = parent_pattern_list.pop(0)
            if ((len(parentPattern.instances) > 1) and (pattern_count < parameters.limit)):
                pattern_count += 1
                extendedPatternList = Pattern.ExtendPattern(parameters, parentPattern)
                while (extendedPatternList):
                    extendedPattern = extendedPatternList.pop(0)
                    if DEBUGFLAG:
                        print("Extended Pattern:")
                        extendedPattern.print_pattern('  ')
                    if (len(extendedPattern.definition.edges) <= parameters.maxSize):
                        # evaluate each extension and add to child list
                        extendedPattern.evaluate(graph)
                        if ((not parameters.prune) or (extendedPattern.value >= parentPattern.value)):
                            Pattern.PatternListInsert(extendedPattern, childPatternList, parameters.beamWidth, parameters.valueBased)
            # add parent pattern to final discovered list
            if (len(parentPattern.definition.edges) >= parameters.minSize):
                Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False) # valueBased = False
        parent_pattern_list = childPatternList
        if not parent_pattern_list:
            print("No more patterns to consider", flush=True)
    # insert any remaining patterns in parent list on to discovered list
    while (parent_pattern_list):
        parentPattern = parent_pattern_list.pop(0)
        if (len(parentPattern.definition.edges) >= parameters.minSize):
            Pattern.PatternListInsert(parentPattern, discoveredPatternList, parameters.numBest, False) # valueBased = False
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