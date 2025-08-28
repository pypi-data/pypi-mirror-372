from plover.steno_dictionary import StenoDictionary
from plover.system.english_stenotype import (
  KEYS,
  IMPLICIT_HYPHEN_KEYS,
  NUMBER_KEY,
  NUMBERS,
)
from plover_stroke import BaseStroke
from struct import unpack

from plover_casecat.translation import ploverify_translation


class Stroke(BaseStroke):
  pass


Stroke.setup(KEYS, IMPLICIT_HYPHEN_KEYS, NUMBER_KEY, NUMBERS)

ENGLISH_STENO_TABLE = "STKPWHRAO*EUFRPBLGTSDZ#(!"

# keys in a stroke are stored in this order, with padding to fill out 32 bits
STENO_KEYMAP = [
  "S-",
  "T-",
  "K-",
  "P-",
  "W-",
  "H-",
  "R-",
  "A-",
  "O-",
  "*",
  "-E",
  "-U",
  "-F",
  "-R",
  "-P",
  "-B",
  "-L",
  "-G",
  "-T",
  "-S",
  "-D",
  "-Z",
  "#",
]


class CaseCATalystDictionary(StenoDictionary):
  readonly = True

  def __init__(self):
    super(CaseCATalystDictionary, self).__init__()

  def __setitem__(self, key, value):
    raise NotImplementedError()

  def __delitem__(self, key):
    raise NotImplementedError()

  def _load(self, filename):
    entries = {}

    with open(filename, "rb") as f:
      f.seek(0x122)
      steno_table = f.read(32)
      assert steno_table.decode("utf-8").rstrip("\x00") == ENGLISH_STENO_TABLE

      f.seek(0x280)

      while True:
        header = f.read(18)
        if header is None or len(header) != 18:
          break

        outline_len = unpack("<B", f.read(1))[0]
        translation_len = unpack("<H", f.read(2))[0]

        outline = []
        for _ in range(outline_len):
          stroke = unpack(">L", f.read(4))[0]
          stroke_bits = f"{stroke:032b}"
          keys = [key for i, key in enumerate(STENO_KEYMAP) if stroke_bits[i] == "1"]
          outline.append(str(Stroke.from_keys(keys)))

        translation = f.read(translation_len)
        try:
          entries[tuple(outline)] = ploverify_translation(translation)
        except ValueError:
          # this entry contains CaseCAT-specific functionality we don't care about
          pass

        pad = f.tell() % 4
        if pad:
          f.read(4 - pad)

    self.update(entries.items())
