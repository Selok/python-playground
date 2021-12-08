import re
import itertools
from enum import Enum
from typing import Dict, List

import numpy as np
import pandas as pd
from metaphone import doublemetaphone

SCHEMA = np.dtype([
    ("character", 'O'),
    ("phonetics", 'O')
])

PHONETIC_DICT: pd.DataFrame = None

LATIN_REGEX = re.compile(
    u'[0-9A-Za-z\u00C0-\u00D6\u00D8-\u00f6\u00f8-\u00ff\\s]')


class PhoneticResult(Enum):
    EXACT_SAME = 2
    SIMILAR = 1
    NON_RELATED = 0

    def __ge__(self, other):
        # pylint: disable=W0143
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        # pylint: disable=W0143
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        # pylint: disable=W0143
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        # pylint: disable=W0143
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


def _translate(word: str) -> List[str]:
    transcription = []
    is_last_latin = False
    for c in list(word.strip()):

        if not c.strip():
            is_last_latin = False
            continue
        elif LATIN_REGEX.match(c):
            if is_last_latin:
                s = transcription[-1][0]
                transcription[-1][0] = s + c
            else:
                transcription.append([c])
            is_last_latin = True
        else:
            p_series = []
            for p in PHONETIC_DICT[PHONETIC_DICT.character == c]['phonetics']:
                p_series.extend(p)
            is_last_latin = False
            transcription.append(p_series)
    res = []
    for v in list(itertools.product(*transcription)):
        res.append(' '.join(map(str, v)))
    return res


def generate_dictionary(mapping: Dict[str, List[str]], dict_path: str):
    # pylint: disable=W0603
    global PHONETIC_DICT

    data = np.array(list(mapping.items()), dtype=SCHEMA)
    PHONETIC_DICT = pd.DataFrame(data)
    PHONETIC_DICT.to_pickle(dict_path)


def load_phonetic_dictionary(data_path: str):
    # pylint: disable=W0603
    global PHONETIC_DICT

    PHONETIC_DICT = pd.read_pickle(data_path)


def is_phonetic_similar(subject: str, target: str) -> PhoneticResult:
    if PHONETIC_DICT is None:
        return PhoneticResult.NON_RELATED

    subject_trans = _translate(subject)
    target_trans = _translate(target)

    if set(subject_trans).intersection(target_trans):
        return PhoneticResult.EXACT_SAME

    subject_dm = []
    for transcription in subject_trans:
        code = doublemetaphone(transcription.replace(' ', ''))
        if code:
            subject_dm.extend([c for c in code if c])

    target_dm = []
    for transcription in target_trans:
        code = doublemetaphone(transcription.replace(' ', ''))
        if code:
            target_dm.extend([c for c in code if c])

    if set(target_dm).intersection(subject_dm):
        return PhoneticResult.SIMILAR

    return PhoneticResult.NON_RELATED


def is_phonetic_included(subject: str, target: str) -> bool:
    if subject == target:
        return True

    if PHONETIC_DICT is None:
        return False

    transcription: str
    trans = []
    for transcription in _translate(subject):
        subject_tran = transcription.split(' ')
        trans.append(subject_tran)

    for transcription in _translate(target):
        target_tran = transcription.split(' ')
        target_tran_set = set(target_tran)
        for st in trans:
            subject_tran = ' '.join([c for c in st if c in target_tran_set])
            if subject_tran == transcription:
                return True

    return False
