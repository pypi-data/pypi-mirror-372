import os
import importlib.resources


def count_flex(ligand_inp_file_path):
    # Counts the number of times FLEDIH appears in
    optimz_list = [[9999, '-', -1], [9999, '-', 0]]
    with open(ligand_inp_file_path, 'r') as t:
        lines = t.readlines()
        count = 0
        for line in lines:
            if line[0] == 'F':
                count += 1
                optimz_list.append([9999, '-', count])
    return optimz_list


def write_config_file(target_inp_path, ligand_inp_path, binding_site_path, config_file_folder_path,
                      output_file_name='config', **kwargs):
    """
    Generates a configuration file with default values that can be
    overridden by keyword arguments.

    Args:
        config_file_folder_path (str): Path to the output folder.
        output_file_name (str): Name of the output file.
        target_inp_path (str): Path to the target input file (generated with processligand-py).
        ligand_inp_path (str): Path to the ligand input file (generated with processligand-py).
        binding_site_path (str): Path to the binding site file (generated with getcleft-py).
        **kwargs: Keyword arguments to override defaults. For flags like 'NOINTR', set False to disable.
    Returns:
        Path to the generated configuration file.

    """
    if not os.path.exists(config_file_folder_path):
        raise FileNotFoundError(f"Output folder '{config_file_folder_path}' does not exist.")
    if not os.path.exists(target_inp_path):
        raise FileNotFoundError(f"Target input file '{target_inp_path}' does not exist.")
    if not os.path.exists(ligand_inp_path):
        raise FileNotFoundError(f"Ligand input file '{ligand_inp_path}' does not exist.")
    if not os.path.exists(binding_site_path):
        raise FileNotFoundError(f"Binding site file '{binding_site_path}' does not exist.")
    config_file_output_path = os.path.join(config_file_folder_path, f'{output_file_name}.inp')
    deps_path = importlib.resources.files('flexaidpy').joinpath('deps')
    matrix_path = importlib.resources.files('flexaidpy').joinpath('deps', 'MC_st0r5.2_6.dat')
    optimz_list = count_flex(ligand_inp_path)
    default_options = {
        'INPLIG': ligand_inp_path,
        'METOPT': 'GA',
        'OPTIMZ': optimz_list,
        'PDBNAM': target_inp_path,
        'RNGOPT': f'LOCCLF {binding_site_path}',
        'ACSWEI': False,
        'BPKENM': False,
        'CLRMSD': False,
        'CLUSTA': False,
        'COMPLF': 'VCT',
        'CONSTR': False,
        'DEECLA': False,
        'DEEFLX': False,
        'DEFTYP': False,
        'DEPSPA': deps_path,
        'EXCHET': False,
        'FLEXSC': False,
        'HTPMOD': False,
        'IMATRX': matrix_path,
        'INCHOH': False,
        'INTRAF': False,
        'MAXRES': 10,
        'NMAAMP': False,
        'NMAEIG': False,
        'NMAMOD': False,
        'NOINTR': True,
        'NORMAR': True,
        'NRGOUT': False,
        'NRGSUI': False,
        'OMITBU': False,
        'OUTRNG': False,
        'PERMEA': 0.9,
        'RMSDST': False,
        'ROTOBS': False,
        'ROTOUT': False,
        'ROTPER': False,
        'SCOLIG': False,
        'SCOOUT': False,
        'SLVTYP': 40,
        'SLVPEN': False,
        'SPACER': 0.375,
        'STATEP': False,
        'TEMPER': False,
        'TEMPOP': False,
        'USEACS': False,
        'USEDEE': False,
        'VARANG': 5.0,
        'VARDIS': False,
        'VARDIH': 5.0,
        'VARFLX': 10.0,
        'VCTPLA': 'R',
        'VCTSCO': False,
        'VINDEX': True
    }

    config = default_options.copy()
    config.update(kwargs)

    output_lines = []
    for key, value in config.items():
        if value is None or value is False:
            continue
        elif value is True:
            output_lines.append(key)
        elif key == 'OPTIMZ' and isinstance(value, list):
            for item in value:
                output_lines.append(f"{key} {' '.join(map(str, item))}")
        else:
            output_lines.append(f"{key} {value}")

    output_lines.append('ENDINP')
    with open(config_file_output_path, 'w') as f:
        f.write('\n'.join(output_lines))
    return config_file_output_path
