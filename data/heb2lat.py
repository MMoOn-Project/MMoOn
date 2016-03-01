#!/usr/bin/python3


import string
import unicodedata

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

vowel = {
    "\u05b0": "m",
    "\u05b4": "i",
    "\u05b5": "e",
    "\u05b6": "n",
    "\u05b1": "n",
    "\u05b2": "a",
    "\u05b7": "a",
    "\u05b8": "t",
    "\u05b9": "o",
    "\u05bb": "u",
}

alephbetOne = consonants

class glyph:
    consonant = '_'     # a-z
    position = 0        # 0-2,89
    vowel = '-'         # a-z
    length = 3          # 3-7
    stress = False      # (True, False) "."
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
            g = glyph()
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

text = "hallo äöü ÄÖÜ HALLO לכד אָכּלֻץ אָאּגּהּ ְ ◌ שׁ שׂ ש"
text2 = "Schulter כָּתֵף"
text2 = "Schulter כָּ"
text3 = "Schulter כָּ"
trans = heb2lat(text);
print("\n")
trans2 = heb2lat(text2);
print("\n")
trans2 = heb2lat(text3);

print(text)
print(trans)

print(text2)
print(trans2)

# TODO 4 Eindeutigkeits-Modi:
# Maximale Eindeutigkeit (Breite 4-5) K0t3
# Cases Sensitive Eindeutigkeit (Breite 2-5)  Kt
# Cases Insensitive Eindeutigkeit (Breite 4-5)  k0t3
# Kompakt (auch eindeutig, Breite 2-5) kt
