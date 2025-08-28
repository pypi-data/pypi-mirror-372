import sys

from datasets import Dataset, load_dataset
from datasets.utils.logging import disable_progress_bar

disable_progress_bar()

MONA_ORIGIN = r"""
            ／￣￣￣￣￣￣＼
            |   You guys   |
     ∩__∩   |   have too   |
   ( ´ー`) <   much spare  |
   (     )  |    time.     |
    | | |   |              |
   (__)__)  ＼＿＿＿＿＿＿／
"""


def load_ascii_dataset() -> Dataset:
    ds = load_dataset(
        'pielet/ascii-cats', data_files='data/ascii-cats.jsonl', split='train'
    )
    return ds


def main() -> None:
    if len(sys.argv) == 1:
        print(MONA_ORIGIN)
        return

    ds = load_ascii_dataset()

    if sys.argv[1] == 'list':
        print('Available cats:', ', '.join(sorted(ds['name'])))
        return

    cat_name = ' '.join(arg for arg in sys.argv[1:]).strip()
    result = ds.filter(lambda x: x['name'].lower() == cat_name.lower())

    if len(result) > 0:
        print(result[0]['ascii'])
    else:
        print('Cat not found. Try `ascii-cat list`.')
