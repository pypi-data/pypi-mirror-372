from pydantic import BaseModel
from pytextrust import pytextrust
from typing import List, Union
import json
from pathlib import Path


class LiteralEntity(BaseModel):
    name: str
    literals: List[str]
    public: bool
    type: str = 'Literal'


class RegexEntity(BaseModel):
    name: str
    patterns: List[str]
    type: str = 'Regex'


class EntitySystemDump(BaseModel):
    folder: str
    entities: List[Union[LiteralEntity, RegexEntity]]

    def perform_dump(self):
        result = pytextrust.wrap_entity_dump(self.json())

        return result


# PLOT ENTITIES
# prefix components:
space = '    '
branch = '│   '
# pointers:
tee = '├── '
last = '└── '


def tree(dir_path: Path, prefix: str = ''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        if path.is_file():
            with open(path, mode='rb') as file:
                aux = json.load(file)
                ent_type = aux.get('type').replace(
                    'Regex', 'RE').replace('Literal', 'LIT')
                if ent_type == 'LIT':
                    is_public = aux.get('public', False)
                    public_str = "public" if is_public else "private"
                    ent_type += f" {public_str}"
                to_add = ' - ' + ent_type
                to_add += f" - {len(aux.get('literals', aux.get('patterns', [])))}"
                to_print = prefix + pointer + path.name + to_add
        else:
            to_add = '\x1b[0m'
            to_print = prefix + pointer + '\033[1m' + path.name + to_add
        yield to_print
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)


def print_ents(path):
    print('\033[1m' + path + '\x1b[0m')
    for line in tree(Path(path)):
        print(line)


class EntitySystemApply(BaseModel):
    texts: List[str]
    system_load_folder: str = None
    extra_entities: List[Union[LiteralEntity, RegexEntity]] = None
    substitute_bound: bool
    substitute_latin_char: bool
    case_insensitive: bool
    unicode: bool
    regexset_chunk_size: int
    regexset_size_limit: int
    regexset_dfa_size_limit: int
    n_threads: int = -1
    text_chunk_size: int = 10000

    def apply_system(self):
        if self.extra_entities is None:
            self.extra_entities = []
        result = pytextrust.wrap_entity_system_apply(self.json())
        results_dict = json.loads(result)

        return results_dict
