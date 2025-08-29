import numpy as np
import pytest
from mmap_ninja.ragged import RaggedMmap
from mmap_ninja.string import StringsMmap
from transformers import BertTokenizerFast

from mmap_ninja_dataframe import generate_batches
from mmap_ninja_dataframe.base import _create_mmap_for_key
from mmap_ninja_dataframe.dense import DataFrameMmap



class Yo:
    pass


def test_creation_with_strings(tmp_path):
    dicts = [
        {'description': 'He talked for so long.', 'tokens': [1, 2, 3, 9]},
        {'description': 'She was sorry.', 'tokens': [91, 23]}
    ]
    dataframe_mmap = DataFrameMmap.from_list_of_dicts(
        out_dir=tmp_path / 'alternative',
        dicts=dicts,
        mode='sample',
        verbose=True
    )
    assert isinstance(dataframe_mmap['description'], StringsMmap)
    assert isinstance(dataframe_mmap['tokens'], RaggedMmap)
    assert isinstance(dataframe_mmap[1], dict)

    with pytest.raises(ValueError):
        dataframe_mmap[Yo()]


def test_creation_with_different_shapes(tmp_path):
    dicts = [
        {'description': 'He talked for so long.', 'tokens': [1, 2, 3, 9]},
        {'description': 'She was sorry.', 'tokens': Yo()}
    ]
    with pytest.raises(ValueError):
        dataframe_mmap = DataFrameMmap.from_list_of_dicts(
            out_dir=tmp_path / 'alternative',
            dicts=dicts,
            mode='sample',
            verbose=True
        )


def test_creation_with_different_types(tmp_path):
    dicts = [
        {'description': 'He talked for so long.', 'tokens': Yo()},
        {'description': 'She was sorry.', 'tokens': Yo()}
    ]
    with pytest.raises(ValueError):
        dataframe_mmap = DataFrameMmap.from_list_of_dicts(
            out_dir=tmp_path / 'alternative',
            dicts=dicts,
            mode='sample',
            verbose=True
        )


def test_creation_ragged(tmp_path):
    dicts = [
        {'description': 'He talked for so long.', 'tokens': np.array([1, 2, 3])},
        {'description': 'She was sorry.', 'tokens': np.array([0, 1])}
    ]
    dataframe_mmap = DataFrameMmap.from_list_of_dicts(
        out_dir=tmp_path / 'alternative',
        dicts=dicts,
        mode='sample',
        verbose=True
    )
    assert isinstance(dataframe_mmap['tokens'], RaggedMmap)


def generator_of_samples():
    for i in range(1, 100):
        yield {'description': f'descr{i}', 'tokens': np.zeros(i), 'index': i}


def test_create_from_generator(tmp_path):
    DataFrameMmap.from_generator(
        out_dir=tmp_path / 'alternative',
        sample_generator=generator_of_samples(),
        batch_size=32,
        mode='sample',
        verbose=True
    )

    df = DataFrameMmap(tmp_path / 'alternative', target_keys=['tokens'])
    assert 'idx' in df[0]
    assert 'tasks' in df[1]
    assert len(df) == 99


def test_create_from_huggingface_tokenization(tmp_path):
    tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")
    texts = [
        'This is the first text',
        'Foo bar to yo asdasdasdasd asdasda',
        "We went to the dentist",
        "Spiderman is a superhero.",
        "Ilya e pich.",
        "Prodavam zelki",
    ]

    df_mmap = DataFrameMmap.from_generator(
        out_dir=tmp_path / 'df_mmap',
        sample_generator=generate_batches(tokenizer, texts, 4),
        batch_size=2,
        mode='batch',
        verbose=True
    )

    assert ['attention_mask', 'input_ids', 'token_type_ids'] == df_mmap.get_columns()

    with pytest.raises(ValueError):
        DataFrameMmap.from_generator(
            out_dir=tmp_path / 'df_mmap',
            sample_generator=generate_batches(tokenizer, texts, 4),
            batch_size=2,
            mode='something',
            verbose=True
        )


def test_performance(tmp_path):
    batch = [
        {'description': 'He talked for so long.', 'tokens': np.array([1, 2, 3])},
        {'description': 'She was sorry.', 'tokens': np.array([0, 1])}
    ]
    dicts = []
    for _ in range(10_000):
        dicts.extend(batch)
    dataframe_mmap = DataFrameMmap.from_generator(
        out_dir=tmp_path / 'alternative',
        sample_generator=dicts,
        mode='sample',
        batch_size=64,
        verbose=True
    )
    assert isinstance(dataframe_mmap['tokens'], RaggedMmap)
    assert dataframe_mmap[-1].keys() == dicts[-1].keys()
    dataframe_mmap.append(batch[0])

    # Test that adding a new does not crash the opener.
    path = (tmp_path / 'alternative' / 'dumb.txt')
    path.write_text('Something')
    df = DataFrameMmap(tmp_path / 'alternative')
    assert len(df) == len(dataframe_mmap)


def test_create_datetime(tmp_path):
    dates_str = [
        '2005-12-01',
        '2012-03-03'
    ]
    generator = list(map(np.datetime64, dates_str))
    _create_mmap_for_key(tmp_path / 'out', key='datetime_out', values=generator, verbose=True)
