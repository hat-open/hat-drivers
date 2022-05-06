from pathlib import Path
import click
import re
import sys

from hat import json

from pysmi.reader import FileReader
from pysmi.writer import CallbackWriter
from pysmi.parser import SmiStarParser
from pysmi.codegen import JsonCodeGen
from pysmi.compiler import MibCompiler


@click.group()
def main():
    pass


@main.command()
@click.option('--path', default=None, type=Path, required=True)
@click.option('--out-path', default=None, type=Path)
@click.option('--silent', default=False, type=bool, is_flag=True)
def get_all(path, out_path, silent):
    verbose = not silent
    mibs_json = mibs_to_json(path, verbose)

    if verbose:
        print_mibs_tree(mibs_json)
        # print_node_type_stats(mibs_json)

    if out_path:
        json.encode_file(mibs_json, out_path)


@main.command()
@click.option('--oid', default=None, type=str, required=True)
@click.option('--path', default=None, type=Path, required=True)
@click.option('--verbose', default=False, type=bool, is_flag=True)
def translate(oid, path, verbose):
    mib_json = mibs_to_json(path, verbose)
    tree = mib_tree(mib_json)
    path = translate_oid(oid, tree, verbose)
    descr = json.get(tree, [*oid.split('.'), 'description'],
                     'no description found')
    print(f"{path}\n\n  description: {descr}")


def translate_oid(oid, mib_tree, verbose=False):
    oid_path = oid.split('.')
    name_path = []
    for idx, i in enumerate(oid_path):
        node_name_path = [*oid_path[:idx + 1], 'name']
        name = json.get(mib_tree, node_name_path, i)
        if idx == 0 and i == '1':
            name = 'iso'
        name_path.append(name)
    oid_translated = '.'.join(name_path)
    return oid_translated


def mibs_to_json(path, verbose):
    all_mibs = get_all_mibs(path)

    inputMibs = list(all_mibs.keys())
    mib_src_dirs = set(p.parent for p in all_mibs.values())

    res_json = []

    def writer(mibName, jsonDoc, cbCtx):
        res_json.append(json.decode(jsonDoc))

    mibCompiler = MibCompiler(
        SmiStarParser(), JsonCodeGen(), CallbackWriter(writer))

    # search for source MIBs here
    mibCompiler.addSources(*[FileReader(i) for i in mib_src_dirs])

    # run recursive MIB compilation
    results = mibCompiler.compile(*inputMibs, ignoreErrors=True, genTexts=True)
    res_dict = {}
    for k, v in results.items():
        res_dict[v] = res_dict.get(v, []) + [k]

    if verbose:
        print(f'compile results: \n')
        for k, v in res_dict.items():
            print(f"{k}:")
            for i in v:
                print(f"\t{i}")

    return res_json


def oids_from_mibs_json(mibs_json):
    return [i for mib in mibs_json for i in mib.values() if i.get('oid')]


def print_mibs_tree(mibs_json):
    print('\nmibs tree:')
    mibs_sorted = sorted(oids_from_mibs_json(mibs_json),
                         key=lambda j: j['oid'])
    for item in mibs_sorted:
        oid = item['oid']
        name = item['name']
        if oid.startswith('1') and len(oid.split('.')) == 2:
            print('iso')
        level = oid.count('.')
        node_type = (json.get(item, ['syntax', 'type'])
                     if item.get('class') == 'objecttype'
                     else item.get('class'))
        print('  ' * (level - 1) + f"|_{name} ({oid}) {node_type}")


def mib_tree(mibs_json):
    tree = {}
    for item in sorted(oids_from_mibs_json(mibs_json), key=lambda j: j['oid']):
        tree = json.set_(tree, item['oid'].split('.'), item)
    return tree


def print_node_type_stats(mibs_json):
    print('\nmib node types:')
    node_types = []
    for item in oids_from_mibs_json(mibs_json):
        node_type = (json.get(item, ['syntax', 'type'])
                     if item.get('class') == 'objecttype'
                     else item.get('class'))
        if node_type:
            node_types.append(node_type)
    for nt in sorted(set(node_types)):
        print(f"\t{nt} {node_types.count(nt)}")


def get_mib_name_from_file(path: Path):
    """Returns the MIB name from the MIB file."""
    with open(path) as f:
        try:
            for line in f:
                line = line.strip()
                match = re.search(
                    r"^([\w-]+)\s+DEFINITIONS\s*::=\s*BEGIN", line)
                if match:
                    return match[1]
        except UnicodeDecodeError:
            return None
    return None


def get_all_mibs(path: Path):
    """Returns all MIB names with their file names."""
    mib_files: dict = {}
    for p in path.glob("*"):
        if p.is_file():
            mib_name = get_mib_name_from_file(p)
            if mib_name:
                mib_files[mib_name] = p
        elif p.is_dir():
            mib_files.update(get_all_mibs(p))
    return mib_files


if __name__ == "__main__":
    sys.exit(main())
