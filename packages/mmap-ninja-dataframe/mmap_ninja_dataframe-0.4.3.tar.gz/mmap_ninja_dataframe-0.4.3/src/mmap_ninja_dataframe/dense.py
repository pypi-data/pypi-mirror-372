from pathlib import Path
from typing import Union, Dict, Callable, List, Optional

import numpy as np
from mmap_ninja import base, numpy as np_ninja

from .base import _list_of_dicts_to_dict_of_lists, _create_mmap_for_key, _load_dir_as_dict


class DataFrameMmap:

    def __init__(
            self,
            out_dir: Union[str, Path],
            wrapper_fn_dict: Dict[str, Callable] = None,
            subset: Optional[List[str]] = None,
            target_keys: Optional[List[str]] = None,
            mode: str = 'r+b',
    ):
        self._out_dir = Path(out_dir)
        self._wrapper_fn_dict = {} if wrapper_fn_dict is None else wrapper_fn_dict
        self._subset = subset
        self._mode = mode
        self._data = self._load_dir_as_dict()
        self._target_keys = set(target_keys) if target_keys else None

    def get_columns(self) -> List[str]:
        return list(self._data)

    def get_column(self, item: str):
        return self._data[item]

    def get_sample(self, item: int) -> Dict:
        res = {}
        tasks = []
        for key, value in self._data.items():
            res[key] = value[item]
            if self._target_keys and key in self._target_keys:
                tasks.append(key)
        if self._target_keys:
            res['idx'] = item
            res['tasks'] = tasks
        return res

    def get_samples(self):
        for i in range(len(self)):
            yield self.get_sample(i)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.get_column(item)
        if isinstance(item, int):
            return self.get_sample(item)
        if np.isscalar(item):
            return self.get_sample(item)
        raise ValueError(f'__getitem__ argument should be either a str, or an int.')

    def __len__(self):
        return len(next(iter(self._data.values())))

    def append(self, dct: Dict):
        self.extend([dct])

    def extend(self, dicts: List[Dict]):
        dict_of_lists = _list_of_dicts_to_dict_of_lists(dicts, 'sample')
        self.extend_with_list_of_dicts(dict_of_lists)

    def extend_with_list_of_dicts(self, dict_of_lists):
        for k, mmap in self._data.items():
            new_value = dict_of_lists[k]
            if isinstance(mmap, np.memmap):
                np_ninja.extend(mmap, np.asarray(new_value))
            else:
                mmap.extend(new_value)
        self._data = self._load_dir_as_dict()

    def _load_dir_as_dict(self):
        return _load_dir_as_dict(self._out_dir, self._wrapper_fn_dict, self._subset, self._mode)

    @classmethod
    def from_list_of_dicts(
            cls,
            out_dir: Union[str, Path],
            dicts: List[Dict],
            mode: str,
            verbose=False
    ):
        dict_of_lists = _list_of_dicts_to_dict_of_lists(dicts, mode=mode, verbose=verbose)
        return cls.from_dict_of_lists(out_dir, dict_of_lists, verbose=verbose)

    @classmethod
    def from_dict_of_lists(
            cls,
            out_dir: Union[str, Path],
            dict_of_lists: Dict[str, List],
            verbose=False
    ):
        """
        Creates a new DataFrameMmap from a dictionary of lists.

        :param out_dir: The output directory
        :param dict_of_lists: The dictionary of lists
        :param verbose: Whether to print progress and show additional information.
        :return: The DataFrameMmap instance
        """
        out_dir = Path(out_dir)
        out_dir.mkdir(exist_ok=True)
        for key, values in dict_of_lists.items():
            _create_mmap_for_key(out_dir, key, values, verbose)
        return cls(out_dir)

    @classmethod
    def from_generator(
            cls,
            out_dir: Union[str, Path],
            sample_generator,
            mode: str,
            batch_size: int,
            verbose=False
    ):
        """
        Creates a new DataFrameMmap from the samples yielded by a generator.

        :param out_dir: The output directory, which will persist the memory map.
        :param sample_generator: The generator, which yields dicts.
        :param mode: Either "sample" or "batch". "sample" should be used when the values of the dict is one sample,
        while "batch" should be used when the values of the dict is a list of samples.
        :param batch_size: The number of samples to be kept in memory before being flushed to disk.
        :param verbose: Whether to print progress and show additional information.
        :return: The DataFrameMmap instance
        """
        return base.from_generator_base(
            out_dir=out_dir,
            sample_generator=sample_generator,
            batch_size=batch_size,
            mode=mode,
            verbose=verbose,
            batch_ctor=cls.from_list_of_dicts,
        )
