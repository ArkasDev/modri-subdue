class ParametersSubdueC:

    def __init__(self):
        self.outputFileName = ""
        self.beamWidth = 4
        self.iterations = 1
        # default (0) is |E|/2
        self.limit = 0
        # default (0) is |V|
        self.maxSize = 0
        self.minSize = 1
        self.numBest = 3
        self.overlap = False
        self.prune = False
        self.valueBased = False
        # 1 (MDL), 2 (Size)
        self.eval = 1
        self.undirected = False
        self.experimentFolder = ""
        self.graphPath = ""
        self.subdue_lib_windows_location = ""
