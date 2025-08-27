# FlexAID in a Python Package

A Python package designed to prepare arguments and run `FlexAID`.

---

## Example usage:

```
from flexaidpy import write_config_file, write_ga_file, run_flexaid


config_file_path = write_config_file(
    target_inp_path='/path/to/flexaid_target.inp.pdb',
    ligand_inp_path='/path/to/flexaid_ligand.inp',
    binding_site_path='/path/to/binding_site_sph_.pdb',
    config_file_folder_path='/path/to/folder/where/config/is/written'
    )

# Modifying config parameters for running in high throughput mode: 
# config_file_path = write_config_file(
#     target_inp_path='/path/to/flexaid_target.inp.pdb',
#     ligand_inp_path='/path/to/flexaid_ligand.inp',
#     binding_site_path='/path/to/binding_site_sph_.pdb',
#     config_file_folder_path='/path/to/folder/where/config/is/written',
#     HTPMOD=True, 
#     MAXRES=1
#     )

ga_file_path = write_ga_file(ga_file_folder_path='/path/to/folder/where/ga/is/written')
run_flexaid(config_file_path,
            ga_file_path,
            result_save_path='/path/to/save/results/RESULT_NAME')
```

The `result_save_path` must be an absolute path and include the name the result file will be given without the extension.
In this case the results will be saved in the folder `/path/to/save/results/` and they will be named `RESULT_NAME_0.pdb`, `RESULT_NAME_1.pdb`, etc.

If you wish to see the output of `FlexAID` live to keep track of the progress there the `live_output` flag that can be set to `True`


### A full list of `config` and `ga` parameters is available here:
https://github.com/NRGlab/FlexAID/tree/flexaid-cpp

---
## Args for run_flexaid():

| Parameter            | Description                                                                                                                                                         |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `config_file_path`   | Path to the configuration file that is returned by the `write_config_file()` function.                                                                              |
| `ga_file_path`       | Path to the genetic algorithm (GA) file that is returned by the `write_ga_file()` function.                                                                         |
| `result_save_path`   | Absolute path including the name for saving result files (without extension). Results will be saved as `[result_save_path]_0.pdb`, `[result_save_path]_1.pdb`, etc. |
| `live_output`        | Boolean flag (default: `False`). When set to `True`, FlexAID's output will be displayed in real-time to track progress.                                             |

## Returns

| Type            | Description                                               |
|-----------------|-----------------------------------------------------------|
| `FlexAIDResult` | An object containing `returncode`, `stdout` and `stderr`. |

---

## Full run on a target and ligand using `GetCleft`, `ProcessLigand` and `FlexAiD`:

```
import os
from processligandpy import run_processligand
from flexaidpy import write_config_file, write_ga_file, run_flexaid
from getcleftpy import run_getcleft

file_save_path = '/path/to/folder/with/target_and_ligand'
target_file_path = os.path.join(file_save_path, '2ixd.pdb')
ligand_path = os.path.join(file_save_path, 'ATP_ideal.sdf')
result_save_folder = os.path.join(file_save_path, 'result')
if not os.path.exists(result_save_folder):
    os.makedirs(result_save_folder)
final_result_path = os.path.join(result_save_folder, 'RES')


gc_dictionary = run_getcleft(target_file_path, num_clefts=1)

result_target = run_processligand(file_path=target_file_path, target=True)
result_ligand = run_processligand(file_path=ligand_path, atom_index=90000)

config_file_path = write_config_file(
    target_inp_path=result_target.file_path_dict['INP_PDB'][0],
    ligand_inp_path=result_ligand.file_path_dict['INP'][0],
    binding_site_path=gc_dictionary.file_path_dict['SPH'][0],
    config_file_folder_path=file_save_path,
    MAXRES=1,
    HTPMOD=True
)
ga_file_path = write_ga_file(
    ga_file_folder_path=file_save_path,
    NUMCHROM=500,
    NUMGENER=500,
    PRINTCHR=1,
    PRINTINT=1
)
result = run_flexaid(
    config_file_path,
    ga_file_path,
    result_save_path=final_result_path
)
```