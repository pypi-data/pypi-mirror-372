import os


def write_ga_file(ga_file_folder_path, file_name='ga_inp', **kwargs):
    """
    Generates a ga configuration file with default values that can be
    overridden by keyword arguments. See readme for more details.

    Args:
        ga_file_folder_path (str): Folder where to write the GA configuration file
        file_name (str): Name of the file to write (default is 'ga_inp.dat')
        **kwargs: Arbitrary keyword arguments to override defaults.
    Returns:
        Path to the generated ga configuration file.
    """
    if not os.path.exists(ga_file_folder_path):
        raise FileNotFoundError(f"Output folder '{ga_file_folder_path}' does not exist.")
    ga_file_output_path = os.path.join(ga_file_folder_path, f'{file_name}.dat')

    default_options = {
        'NUMCHROM': 500,
        'NUMGENER': 500,
        'ADAPTVGA': 1,
        'ADAPTKCO': [0.95, 0.10, 0.95, 0.10],
        'CROSRATE': 0.90,
        'MUTARATE': 0.025,
        'POPINIMT': 'RANDOM',
        'FITMODEL': 'PSHARE',
        'SHAREALF': 4.0,
        'SHAREPEK': 5.0,
        'SHARESCL': 10.0,
        'REPMODEL': 'BOOM',
        'BOOMFRAC': 1.0,
        'PRINTCHR': 5,
        'PRINTINT': 1,
        'OUTGENER': 1,
    }

    config = default_options.copy()
    config.update(kwargs)

    output_lines = []
    for key, value in config.items():
        if key == 'ADAPTKCO':
            output_lines.append(f"{key} {' '.join(str(x) for x in value)}")
        else:
            output_lines.append(f"{key} {value}")
    with open(ga_file_output_path, 'w') as f:
        f.write('\n'.join(output_lines))
    return ga_file_output_path
