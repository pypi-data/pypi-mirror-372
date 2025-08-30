"""
Handle scripts.
- getopt_printer: prints getopt input in a readable way.
- getopt_reader:  automatically parse getopt opts using tidypath
- incompleted_programs_shell_script: Creates or prins sh script for programs that were not completed. To be used after 'delete_stdin_files'.
- parse_optuna_output: Parses the output file of an Optuna optimization process and returns a sorted DataFrame.
"""
import os
import re
import pandas as pd
from tidypath import fmt

def getopt_printer(opts):
    """Prints getopt input in a readable way."""
    print('\n'.join(f'{opt} => {arg}' for opt, arg in (("Args", "Values"), *opts)))

def getopt_reader(opts, key_short, key_long, print_result=True):
    """
    Returns dict containing opts. args are parsed by tidypath.fmt.decoder.
    NOTE: If not sure about the parsing, do not use it.
    """
    key_short_fmt = [f"-{k}" for k in key_short.split(":")[:-1]]
    key_long_fmt = [k[:-1] for k in key_long]
    env = {}
    for opt, arg in opts:
        for ks, kl in zip(key_short_fmt, key_long_fmt):
            if opt in (ks, f"--{kl}"):
                env[kl.replace("-", "_")] = fmt.decoder(arg)
                break
    if print_result:
        print(f"getopt_reader result:\n{env}")
    return env

def incompleted_programs_shell_script(script, save_path=None, save_sh=True, stdin_identifier=None, cores=1, memory=4, gpus=0, time="0:20",
                                      programs_dir="nuredduna_programmes/", sh_dir="nuredduna_programmes/", stdin_dir='stdin_files/',
                                      ext='.out', lang="python", shell="bash"):
    """
    Creates or prins sh script for programs that were not completed. To be used after 'delete_stdin_files'.

    Attributes:
        - script:           program name
        - save_path:        None  =>  path = 'script_name'_incompleted.sh
                            path  =>  stores sh in path location
        - save_sh:          True  =>  saves sh in 'save_path'.
                            False =>  prints sh
        - stdin_identifier: if there are stdin files of multiple programs, select only the programs containing 'stdin_identifier'.
    """
    if not ext.startswith("."):
        ext = f".{ext}"
    if lang == 'python':
        script_name, script_ext = os.path.splitext(script)
        if script_ext != ".py":
            script = f"{script_name}.py"

    if gpus:
        hardware_specs = f"-c {cores} -m {memory} -g {gpus} -t {time}"
    else:
        hardware_specs = f"-c {cores} -m {memory} -t {time}"

    def run_command(args):
        stdin_name = os.path.join(stdin_dir, "_".join(args).replace("-", "").replace(" ", "-"))
        args_specs = " ".join(args)
        run_cmd = f'run {hardware_specs} -o {stdin_name}.out -e {stdin_name}.err "{lang} {script} {args_specs}"'
        return run_cmd

    stdin_dir_full = os.path.join(programs_dir, stdin_dir)
    programs = []
    for file in os.listdir(stdin_dir_full):
        if stdin_identifier is None or stdin_identifier in file:
            if os.path.splitext(file)[1] == ext:
                with open(os.path.join(stdin_dir_full, file)) as f:
                    args = []
                    for line in f.readlines()[1:]:
                        if "=>" in line:
                            arg = line.replace(" =>", "").replace("\n","")
                            args.append(arg)
                    if args:
                        programs.append(run_command(args))

    shell_script = f"#!/bin/{shell}\n\n" + "\n".join(programs)

    if save_sh:
        if save_path is None:
            save_path = os.path.join(programs_dir, sh_dir if sh_dir != programs_dir else '', f"{script_name}_incompleted.sh")
        else:
            file, ext = os.path.splitext(save_path)
            if sh_dir not in file:
                file = os.path.join(sh_dir, file)
            if ext != ".sh":
                save_path = f"{file}.sh"
        with open(save_path, 'w') as f:
            f.write(shell_script)
            f.close()
    else:
        print(shell_script)
    return

def parse_optuna_output(file_path, direction='minimize'):
    """
    Parses the output file of an Optuna optimization process and returns a sorted DataFrame.

    Parameters:
    file_path (str): The path to the output file.
    direction (str, optional): The direction of optimization. Can be 'minimize' or 'maximize'. Defaults to 'minimize'.

    Returns:
    df (pd.DataFrame): A DataFrame containing the trial number, output value, and hyperparameters for each trial, sorted by output value.

    Raises:
    ValueError: If the direction is not 'minimize', 'maximize', or None.
    """
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            trial_number = re.search(r'Trial (\d+)', line)
            output_value = re.search(r'with value: ([\d\.]+)', line)
            hyperparameters = re.search(r'parameters: ({.*})', line)

            if trial_number and output_value and hyperparameters:
                trial_number = int(trial_number.group(1))
                output_value = float(output_value.group(1))
                hyperparameters = eval(hyperparameters.group(1))
                hyperparameters = {f'params_{key}': fmt.decoder(value) for key, value in hyperparameters.items()}

                row = {'number': trial_number, 'value': output_value}
                row.update(hyperparameters)
                data.append(row)

    df = pd.DataFrame(data)
    if direction == 'maximize':
        df = df.sort_values('value', ascending=False)
    elif direction == 'minimize':
        df = df.sort_values('value', ascending=True)
    elif direction is not None:
        raise ValueError(f"Invalid direction: {direction}")
    return df

def cmd_incompleted_scripts(script, pdir='nuredduna_programmes/stdin_files', sleep_time=0, c=1, m=6, g=0, t="4:0", G=None):
    def dict_to_args(d):
        return " ".join([f"-{k} {v}" for k, v in d.items()])
    def dict_to_id(d):
        return "_".join([f"{k}-{v}" for k, v in d.items()])

    if script.endswith(".py"):
        script = os.path.splitext(script)[0]

    stdin_dir = os.path.basename(pdir)
    ID_pattern = f'{stdin_dir}/{script}_'

    run_specs = f"-c {c} -m {m} -g {g} -t {t}"
    if G is not None:
        run_specs += f" -G {G}"

    run_pattern = 'run {} -e {}.err -o {}.out "python {}.py {}"'
    combs = []
    for f in os.listdir(pdir):
        if f.endswith("out"):
            f, _ = os.path.splitext(f)
            # Updated regex to match all key-value pairs, including upper-case and hyphenated values
            pattern = r"(?:_|^)([a-zA-Z])-([0-9a-zA-Z.-]+)(?=_|$)"
            matches = re.findall(pattern, f)
            match_dict = dict(zip(*zip(*matches)))
            ID = ID_pattern + dict_to_id(match_dict)
            cmd = run_pattern.format(run_specs, ID, ID, script, dict_to_args(match_dict))
            combs.append(cmd)
    if sleep_time > 0:
        print(f"\nsleep {sleep_time}\n".join(combs))
    else:
        print("\n".join(combs))
    return  combs
