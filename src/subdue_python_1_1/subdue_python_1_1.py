"""
This is a wrapper script for the Subdue Python v1.1 implementation based on Python 2.7
"""

import os


def run(python_location, subdue_location, parameters):
    prune = '--prune ' if parameters.prune is True else ''
    value_based = '--valuebased ' if parameters.valueBased is True else ''

    if os.name == "posix":
        raise Exception("Subdue python v1.1 wrapper not defined under linux.")

    if os.name == "nt":
        os.system(python_location + " " + subdue_location + " " +
                  '--beam ' + str(parameters.beamWidth) + ' '
                  '--maxSize ' + str(parameters.maxSize) + ' '
                  '--minSize ' + str(parameters.minSize) + ' '
                  '--limit ' + str(parameters.limit) + ' '
                  '--iterations ' + str(parameters.iterations) + ' '
                  '--out ' + str(parameters.outputFileName) + ' '
                  '' + value_based +
                  '' + prune +
                  '--writepattern '
                  '--writeinstances '
                  '' + parameters.inputFileName)


