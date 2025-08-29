import ast
from collections import defaultdict
from pathlib import Path
from typing import Union, Dict, List, Callable, Optional

import numpy as np
from mmap_ninja import numpy as np_ninja
from mmap_ninja.base import Wrapped, from_generator_base
from mmap_ninja.string import StringsMmap

from .base import _create_mmap_for_key, _load_dir_as_dict


def _get_all_keys(dicts):
    all_keys = {}
    for l in dicts:
        all_keys.update(l)
    all_keys = list(all_keys)
    return all_keys


def _find_sample_positions_and_values(all_keys, sample, task_values, lens_dict):
    sample_positions = []
    values_dict = {}
    for key in all_keys:
        value = sample.get(key)
        if value is None:
            continue
        idx_task = len(task_values[key]) + lens_dict[key]
        sample_positions.append((idx_task, key))
        values_dict[key] = value
    return sample_positions, values_dict


def _extract_positions_and_task_values(all_keys, dicts, lens_dict):
    task_values = defaultdict(list)
    positions = []
    for i, dct in enumerate(dicts):
        sample_positions, values_dict = _find_sample_positions_and_values(
            all_keys, dct, task_values, lens_dict
        )
        for k, v in values_dict.items():
            task_values[k].append(v)
        positions.append(sample_positions)
    return positions, dict(task_values)


class SparseDataFrameMmap:

    def __init__(
            self,
            out_dir: Union[str, Path],
            wrapper_fn_dict: Dict[str, Callable] = None,
            subset: Optional[List[str]] = None,
            target_keys: Optional[List[str]] = None,
            mode: str = 'r+b',
    ):
        out_dir = Path(out_dir)
        self._out_dir = out_dir
        self._wrapper_fn_dict = {} if wrapper_fn_dict is None else wrapper_fn_dict
        self._subset = subset
        self._mode = mode
        self._data = self._load_dir_as_dict()
        self._positions = Wrapped(StringsMmap(out_dir / '_positions'), wrapper_fn=ast.literal_eval)
        self._columns = [k for k in self._data if not k.startswith('_')]
        self._target_keys = set(target_keys) if target_keys else None

    def get_columns(self):
        return self._columns

    def get_sample(self, item: int) -> Dict:
        res = {}
        tasks = []
        for idx, key in self._positions[item]:
            res[key] = self._data[key][idx]
            if self._target_keys and key in self._target_keys:
                tasks.append(key)
        if self._target_keys:
            res['idx'] = item
            res['tasks'] = tasks
        return res

    def _load_dir_as_dict(self):
        return _load_dir_as_dict(self._out_dir, self._wrapper_fn_dict, self._subset, self._mode)

    def __getitem__(self, item: int):
        return self.get_sample(item)

    def __len__(self):
        return len(self._positions)

    def append(self, sample: Dict):
        self.extend([sample])

    def extend(self, dicts: List[Dict]):
        all_keys = _get_all_keys(dicts)
        lens_dict = {k: len(self._data[k]) for k in all_keys}
        positions, task_values = _extract_positions_and_task_values(all_keys, dicts, lens_dict)
        self._positions.data.extend(list(map(str, positions)))
        for k in self.get_columns():
            mmap = self._data[k]
            if k not in task_values:
                continue
            new_value = task_values[k]
            if isinstance(mmap, np.memmap):
                np_ninja.extend(mmap, np.asarray(new_value))
            else:
                mmap.extend(new_value)
        self._data = self._load_dir_as_dict()
        self._positions = Wrapped(StringsMmap(self._out_dir / '_positions'), wrapper_fn=ast.literal_eval)

    @classmethod
    def from_list_of_dicts(
            cls,
            out_dir: Union[str, Path],
            dicts: List[Dict],
            verbose=False
    ):
        out_dir = Path(out_dir)
        out_dir.mkdir(exist_ok=True)
        all_keys = _get_all_keys(dicts)
        lens_dict = {k: 0 for k in all_keys}
        positions, task_values = _extract_positions_and_task_values(all_keys, dicts, lens_dict)
        StringsMmap.from_strings(out_dir / '_positions', list(map(str, positions)))
        for key, values in task_values.items():
            _create_mmap_for_key(out_dir, key, values, verbose)
        return cls(out_dir)

    @classmethod
    def from_generator(
            cls,
            out_dir: Union[str, Path],
            sample_generator,
            batch_size: int,
            verbose=False
    ):
        """
        Creates a new SparseDataFrameMmap from the samples yielded by a generator.

        :param out_dir: The output directory, which will persist the memory map.
        :param sample_generator: The generator, which yields dicts.
        :param batch_size: The number of samples to be kept in memory before being flushed to disk.
        :param verbose: Whether to print progress and show additional information.
        :return:
        """
        return from_generator_base(
            out_dir=out_dir,
            sample_generator=sample_generator,
            batch_size=batch_size,
            verbose=verbose,
            batch_ctor=cls.from_list_of_dicts,
        )
