import sys
import time
import json
import theobald_subdue.T_Parameters as Parameters
import theobald_subdue.T_Graph as Graph
import theobald_subdue.T_Pattern as Pattern


def load_graph(input_file_name):
    """
    Read graph from given filename.
    """
    with open(input_file_name, "r") as input_file:
        json_graph = json.load(input_file)
        graph = Graph.Graph()
        graph.load_from_json(json_graph)
    return graph


def substructure_discovery(parameters, graph):
    """
    The main discovery loop. Finds and returns best patterns in given graph.
    """
    # Counter for limit parameter
    pattern_count = 0

    # Get initial one-edge patterns
    parent_patterns = get_initial_patterns(parameters, graph)

    # Store best patterns
    discovered_patterns = []

    # Start another loop if parent patterns are available and the limit has not been reached. Reset child patterns.
    while (pattern_count < parameters.limit) and parent_patterns:
        child_patterns = []

        # Discover patterns for each parent pattern
        while parent_patterns:
            parent_pattern = parent_patterns.pop(0)

            # Skip discovery for the selected parent pattern if:
            #   - limit is reached
            #   - there are no other or only one instance of the parent pattern in the input graph
            #   - max size will be exceeded
            if len(parent_pattern.instances) <= 1 or pattern_count >= parameters.limit or len(parent_pattern.definition.edges) + 1 > parameters.maxSize:
                # Do not add the parent pattern to discovered patterns if min size has not been reached
                if len(parent_pattern.definition.edges) >= parameters.minSize:
                    Pattern.PatternListInsert(parent_pattern, discovered_patterns, parameters.numBest)
                continue

            pattern_count += 1

            # Minimal expansion
            extended_patterns = Pattern.ExtendPattern(parameters, parent_pattern)

            # Evaluate compression for each extended pattern
            while extended_patterns:
                extended_pattern = extended_patterns.pop(0)
                extended_pattern.evaluate(graph)
                if (not parameters.prune) or (extended_pattern.value >= parent_pattern.value):
                    Pattern.PatternListInsert(extended_pattern, child_patterns, parameters.beamWidth)

            #  Do not add the parent pattern to discovered patterns if min size has not been reached
            if len(parent_pattern.definition.edges) >= parameters.minSize:
                Pattern.PatternListInsert(parent_pattern, discovered_patterns, parameters.numBest)

        # When all parent patterns are discovered, move child patterns to discover them in the next round
        parent_patterns = child_patterns

    # Insert any remaining patterns in parent patterns on to discovered patterns
    while parent_patterns:
        parent_pattern = parent_patterns.pop(0)
        if len(parent_pattern.definition.edges) >= parameters.minSize:
            Pattern.PatternListInsert(parent_pattern, discovered_patterns, parameters.numBest)
    return discovered_patterns


def get_initial_patterns(parameters, graph):
    """
    Returns list of single-edge, evaluated patterns in given graph with more than one instance.
    """
    initialPatternList = []
    # Create a graph and an instance for each edge
    edgeGraphInstancePairs = []

    for edge in graph.edges.values():
        graph1 = Graph.CreateGraphFromEdge(edge)

        if parameters.temporal:
            graph1.TemporalOrder()

        instance1 = Pattern.CreateInstanceFromEdge(edge)
        edgeGraphInstancePairs.append((graph1, instance1))

    while edgeGraphInstancePairs:
        edgePair1 = edgeGraphInstancePairs.pop(0)
        graph1 = edgePair1[0]
        instance1 = edgePair1[1]
        pattern = Pattern.Pattern()
        pattern.definition = graph1
        pattern.instances.append(instance1)
        nonmatchingEdgePairs = []

        for edgePair2 in edgeGraphInstancePairs:
            graph2 = edgePair2[0]
            instance2 = edgePair2[1]

            if Graph.GraphMatch(graph1, graph2) and (not Pattern.InstancesOverlap(parameters.overlap, pattern.instances, instance2)):
                pattern.instances.append(instance2)
            else:
                nonmatchingEdgePairs.append(edgePair2)

        if len(pattern.instances) > 1:
            pattern.evaluate(graph)
            initialPatternList.append(pattern)

        edgeGraphInstancePairs = nonmatchingEdgePairs

    return initialPatternList


def theobald_subdue(parameters, graph):
    """
    Top-level function for Subdue that discovers best pattern in graph.
    Optionally, Subdue can then compress the graph with the best pattern, and iterate.

    :param graph: instance of Subdue.Graph
    :param parameters: instance of Subdue.Parameters
    :return: patterns for each iteration -- a list of iterations each containing discovered patterns.
    """
    startTime = time.time()
    iteration = 1
    done = False
    patterns = list()

    while ((iteration <= parameters.iterations) and (not done)):
        iterationStartTime = time.time()
        if (iteration > 1):
            print("----- Iteration " + str(iteration) + " -----\n")
        print("Graph: " + str(len(graph.vertices)) + " vertices, " + str(len(graph.edges)) + " edges")
        patternList = substructure_discovery(parameters, graph)

        if (not patternList):
            done = True
            print("No patterns found.\n")
        else:
            patterns.append(patternList)
            print("\nBest " + str(len(patternList)) + " patterns:\n")
            for pattern in patternList:
                pattern.print_pattern('  ')
                print("")
            # write machine-readable output, if requested
            if (parameters.writePattern):
                outputFileName = parameters.outputFileName + "-pattern-" + str(iteration) + ".json"
                patternList[0].definition.write_to_file(outputFileName)
            if (parameters.writeInstances):
                outputFileName = parameters.outputFileName + "-instances-" + str(iteration) + ".json"
                patternList[0].write_instances_to_file(outputFileName)
            if ((iteration < parameters.iterations) or (parameters.writeCompressed)):
                graph.Compress(iteration, patternList[0])
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
            print("Elapsed time for iteration " + str(iteration) + " = " + str(
                iterationEndTime - iterationStartTime) + " seconds.\n")
        iteration += 1
    endTime = time.time()
    print("SUBDUE done. Elapsed time = " + str(endTime - startTime) + " seconds\n")
    return patterns


def main():
    print("TheobaldSubdue v0.1 \n")

    # Init parameters
    parameters = Parameters.Parameters()
    parameters.set_parameters(sys.argv)

    # Get graph from input file
    graph = load_graph(parameters.inputFileName)

    # Set graph dependent parameters. Graph is required.
    parameters.set_defaults_for_graph(graph)
    parameters.print()

    # Run TheobaldSubdue
    theobald_subdue(parameters, graph)


if __name__ == "__main__":
    main()
