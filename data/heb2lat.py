#!/usr/bin/python3

import string
import unicodedata
import re       # regex

# TODO 4 Eindeutigkeits-Modi:
# Maximale Eindeutigkeit (Breite 4-5) K0t3
# Cases Sensitive Eindeutigkeit (Breite 2-5)  Kt
# Cases Insensitive Eindeutigkeit (Breite 4-5)  k0t3
# Kompakt (auch eindeutig, Breite 2-5) kt

# ISSUES:
# - What about dagesh in final letters? (position = 8 and 9)
# - How to distiguish dagesh qal and dagesh hazak
# - What about sin or shin with dagesh? (position = 1 or 2 and 8)
# - How can we distinguish SEGOL and HATAF SEGOL resp. PATAH and HATAF PATAH

consonants = {
    "א": "a",   # e
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "ה": "h",   # ch
    "ו": "w",
    "ז": "z",
    "ח": "x",  # h     x
    "ט": "t",   # th
    "י": "j",
    "כ": "k",
    "ך": "k",
    "ל": "l",
    "מ": "m",
    "ם": "m",
    "נ": "n",
    "ן": "n",
    "ס": "s",   # sz
    "ע": "y",   # a
    "פ": "p",
    "ף": "p",
    "צ": "c",  #       c
    "ץ": "c",  #       c
    "ק": "q",
    "ר": "r",
    "שׁ": "v", #       v
    "שׂ": "v",  # s    u
    "ש": "v",  #       v
    "ת": "f"   # t     f
}

consonantsReverse = {
     "a" : "א",    # e
     "b" : "ב",
     "g" : "ג",
     "d" : "ד",
     "h" : "ה",    # ch
     "w" : "ו",
     "z" : "ז",
     "x" : "ח",   # h     x
     "t" : "ט",    # th
     "j" : "י",
     "k" : "כ",
     "l" : "ל",
     "m" : "מ",
     "n" : "נ",
     "s" : "ס",    # sz
     "y" : "ע",    # a
     "p" : "פ",
     "c" : "צ",   #       c
     "q" : "ק",
     "r" : "ר",
     "v" : "ש",   #       v
     "f" : "ת",   # t     f
}

consonantsReverseFinal = {
     "k" : "ך",
     "m" : "ם",
     "n" : "ן",
     "p" : "ף",
     "c" : "ץ",
}

vowel = {
    "\u05b0": "m",  # SHEVA (:)
    "\u05b4": "i",  # HIRIQ (.)
    "\u05b5": "e",  # TSERE (..)
    "\u05b6": "n",  # SEGOL (:. dots in a T shape)
    "\u05b1": "n",  # HATAF SEGOL (:. :)
    "\u05b2": "a",  # HATAF PATAH (- :)
    "\u05b7": "a",  # PATAH (-)
    "\u05b8": "t",  # QAMATS (T)
    "\u05b9": "o",  # HOLAM (. on the top)
    "\u05bb": "u",  # QUBUTS (...)
}

vowelReverse = {
    "m": "\u05b0",  # SHEVA (:)
    "i": "\u05b4",  # HIRIQ (.)
    "e": "\u05b5",  # TSERE (..)
    "n": "\u05b6",  # SEGOL (:. dots in a T shape)
    "a": "\u05b7",  # PATAH (-)
    "t": "\u05b8",  # QAMATS (T)
    "o": "\u05b9",  # HOLAM (. on the top)
    "u": "\u05bb",  # QUBUTS (...)
}

alephbetOne = consonants

class Glyph:
    pattern = re.compile('(?P<consonant>[_a-df-hj-np-tb-z])(?P<position>[0-289]{0,1})(?P<vowel>[-aeioutmn])(?P<length>[3-7]{0,1})(?P<stress>[\.]{0,1})', re.IGNORECASE)
    consonant = '_'     # a-z
    position = 0        # 0-2,89
    vowel = '-'         # a-z
    length = 3          # 3-7
    stress = False      # (True, False) "."
    def __init__(self, glyph="_0-3"):
        match = self.pattern.match(glyph)
        self.consonant = match.group('consonant').lower()
        if (not match.group('position') == ""):
            self.position = int(match.group('position'))
        self.vowel = match.group('vowel').lower()
        if (not match.group('length') == ""):
            self.length = int(match.group('length'))
        if (match.group('stress') == "."):
            self.stress = True
    def __repr__(self):
        if (self.length == 3):
            length = ""
        else:
            length = str(self.length)
        if (self.stress):
            stress = "."
        else:
            stress = ""
        if (self.position == 0):
            position = ""
        else:
            position = str(self.position)
        return self.consonant.upper() + position + self.vowel + length + stress
    def toHebrew(self):
        heb = ""
        if self.consonant == "_":
            heb += "\u25cc"    # circle "◌"
        else:
            if (self.consonant.lower() == "v"):
                if self.position == 1:
                    # shin
                    #heb += "ש" + "\u05c1"
                    heb += "שׁ"
                elif self.position == 2:
                    # sin
                    #heb += "ש" + "\u05c2"
                    heb += "שׂ"
                else:
                    heb += "ש"
            elif (self.position == 9):
                heb += consonantsReverseFinal[self.consonant.lower()]
            else:
                heb += consonantsReverse[self.consonant.lower()]
        if (self.position == 8):
            heb += "\u05bc"
        if (not self.vowel == "-"):
            heb += vowelReverse[self.vowel.lower()]
        return heb
    def isNothing(self):
        if (self.consonant == '_' and self.vowel == '-'):
            return True
        return False


def heb2latComp(text):
    for k,v in consonants.items():
        text = text.replace(k,v)
    # shin sin and without dot has to be treated separately because of the order of iterating the alephbet list
    text = text.replace("ש", "sh")

    return text

def heb2lat(text, withSpace=False):
    text = unicodedata.normalize("NFKD", text)
    transliteration = ''
    # iterate through text
    g = None
    line = ""
    for c in text:
        #  find placeholder Kringel replace by "_"
        name = unicodedata.name(c).split(" ")
        category = unicodedata.category(c)
        if category != 'Mn':
            if (g != None and (withSpace or not g.isNothing())):
                    transliteration += str(g)
                    print(line.ljust(90), g, end="\n")
                    line = ""
            g = Glyph()
        if (name[0] == "HEBREW"):
            #  replace letter according to alephbet, caution for shin
            #   check if sofit letter add 9, else 0
            # get punctuation
            #  if no punctuation write "-"
            #  find punctuation
            if (name[1] == "LETTER"):
                line += unicodedata.category(c) + "  " + unicodedata.name(c) + "   "
                if c in consonants:
                    g.consonant = consonants[c]
                if (name[2] == "FINAL"):
                    g.position = 9
            elif (name[1] == "POINT"):
                line += unicodedata.category(c) + "  " + unicodedata.name(c) + "   "
                if c in vowel:
                    g.vowel = vowel[c]
                elif c == "\u05bc":
                    # dagesh or mapiq
                    g.position = 8
                elif c == "\u05c1":
                    # shin
                    g.position = 1
                elif c == "\u05c2":
                    # sin
                    g.position = 2
    if (g != None and (withSpace or not g.isNothing())):
        print(line.ljust(90), g, end="\n")
        line = ""
        transliteration += str(g)
    return transliteration

def lat2heb(text):
    iterator = Glyph.pattern.finditer(text)
    heb = ''
    for match in iterator:
        glyph = Glyph(match.group())
        heb += glyph.toHebrew()
    return heb
