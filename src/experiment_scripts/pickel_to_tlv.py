import sys
import os
import pickle
from compute_components import export_TLV


def load_components_networkx(folder, export_path):
    graphs = []
    for filename in os.listdir(folder):
        if not filename.endswith('.p'):
            continue
        with open(os.path.join(folder, filename), 'rb') as f:  # open in readonly mode
            graph = pickle.load(f)
            graphs.append(graph)
        export_TLV(graphs, export_path)


if __name__ == "__main__":
    input_folder = sys.argv[1]
    export_path = sys.argv[2]
    # export
    load_components_networkx(input_folder, export_path)
