class ParametersSubdueC:

    def __init__(self):
        self.outputFileName = ""      # Same as inputFileName, but with .json removed from end if present
        self.beamWidth = 4            # Number of patterns to retain after each expansion of previous patterns; based on value.
        self.iterations = 1           # Iterations of Subdue's discovery process. If more than 1, Subdue compresses graph with best pattern before next run. If 0, then run until no more compression (i.e., set to |E|).
        self.limit = 0                # Number of patterns considered; default (0) is |E|/2.
        self.maxSize = 0              # Maximum size (#vertices) of a pattern; default (0) is |E|/2.
        self.minSize = 1              # Minimum size (#vertices) of a pattern; default is 1.
        self.numBest = 3              # Number of best patterns to report at end; default is 3.
        self.overlap = False          # Extent that pattern instances can overlap
        self.prune = False            # Remove any patterns that are worse than their parent.
        self.valueBased = False       # Retain all patterns with the top beam best values.
        self.experimentFolder = ""
        self.graphPath = ""
        self.subdue_lib_windows_location = ""
