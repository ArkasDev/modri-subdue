# TheobaldSubdue

## Setup
### Install requirements:
```
pip install guppy3
```

### Prepare your data
You need to create some folders, one for every dataset, in a root folder for your experiment. All folders for the datasets should have a common prefix. In case you have only one dataset, also add a subfolder in your experiment folder.
In each of der folders, there must be a subfolder called `diffgraphs`. The graphs are expected to be given in the `networkx` [JSON format](https://networkx.org/documentation/stable/reference/readwrite/json_graph.html).

You can also provide LineGraph input (one graph datbase in `diffgraphs/db.lg`). 

### Run
Go into the source folder and run:
```
python experiment_runner.py {path_to_your_experiment} {algorithm} {folder_prefix} {graph_input_format}
```

Substitude `{path_to_your_experiment}` by the root folder to your experiment, `{algorithm}` by any of `gaston, gspan, subdue_python` and `{folder_prefix}`, the prefix of the folders in your experiment described in the previous section. For `{graph_input_format}` choose `NX`, if you have a folder with one NetworkX JSON File per graph or `LG`, if you are using LineGraph input.

### Results 
TBD

For each dataset, the results will be put in a subfolder `results` of your dataset.


## Credits
- Subdue Python https://github.com/holderlb/Subdue
- Subdue C https://github.com/gromgull/subdue
- Parsemis https://github.com/timtadh/parsemis
- Parsemis Python Wrapper: https://github.com/tomkdickinson/parsemis_wrapper
