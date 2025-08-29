from collections import defaultdict
from typing import Dict, List

import numpy as np
from mmap_ninja import generic, numpy as np_ninja
from mmap_ninja.ragged import RaggedMmap
from mmap_ninja.string import StringsMmap


def _list_of_dicts_to_dict_of_lists(dicts: List[Dict], mode: str, verbose=False) -> Dict[str, List]:
    task_values = defaultdict(list)
    sequence = dicts
    if verbose:
        from tqdm import tqdm
        sequence = tqdm(dicts)
    for dct in sequence:
        for key, value in dct.items():
            if mode == 'sample':
                task_values[key].append(value)
            elif mode == 'batch':
                task_values[key].extend(value)
            else:
                raise ValueError(f'Unknown mode: "{mode}". Should be either "sample" or "batch".')
    return dict(task_values)


def _load_dir_as_dict(out_dir, wrapper_fn_dict, subset, mode):
    dct = {}
    children = sorted(list(out_dir.iterdir()))
    for path in children:
        if not path.is_dir():
            continue
        key = path.name
        if subset and key not in subset:
            continue
        wrapper_fn = wrapper_fn_dict.get(key)
        dct[key] = generic.open_existing(path, wrapper_fn=wrapper_fn, mode=mode)
    return dct


def _create_ragged_mmap_for_key(out_dir, key, values, verbose):
    if verbose:
        print(f'Key: "{key}" will be converted to a RagedMmap ...')
    RaggedMmap.from_lists(out_dir / key, values)
    if verbose:
        print(f'Key: "{key}" was converted to a RagedMmap.')


def _create_numpy_mmap_for_key(out_dir, key, values, verbose):
    if verbose:
        print(f'Key: "{key}" will be converted to a numpy mmap ...')
    np_values = np.asarray(values)
    np_ninja.from_ndarray(out_dir / key, np_values)
    if verbose:
        print(f'Key: "{key}" was converted to a numpy mmap.')


def _create_stringsmmap_for_key(out_dir, key, values, verbose):
    if verbose:
        print(f'Key: "{key}" will be converted to a StringMmap ...')
    StringsMmap.from_strings(out_dir / key, values)
    if verbose:
        print(f'Key: "{key}" was converted to a StringMmap.')


def _create_mmap_for_key(out_dir, key, values, verbose):
    types = set(type(v) for v in values)
    if len(types) > 1:
        raise ValueError(f'Key: "{key}" has values of different types: {types}.')
    selected_type = next(iter(types))
    if selected_type == str:
        _create_stringsmmap_for_key(out_dir, key, values, verbose)
        return
    if selected_type in [bool, int, float]:
        _create_numpy_mmap_for_key(out_dir, key, values, verbose)
        return
    if np.issubdtype(selected_type, np.number) or selected_type == np.datetime64:
        _create_numpy_mmap_for_key(out_dir, key, values, verbose)
        return
    if selected_type in [list, tuple]:
        _create_ragged_mmap_for_key(out_dir, key, values, verbose)
        return
    if selected_type != np.ndarray:
        raise ValueError(f'Key: "{key}" has unknown selected type: {selected_type}.')
    shapes = set(v.shape for v in values)
    if len(shapes) > 1:
        _create_ragged_mmap_for_key(out_dir, key, values, verbose)
    elif len(shapes) == 1:
        _create_numpy_mmap_for_key(out_dir, key, values, verbose)


def generate_batches(batch_fn, data, batch_size):
    for i in range(0, len(data), batch_size):
        yield batch_fn(data[i: i + batch_size])
