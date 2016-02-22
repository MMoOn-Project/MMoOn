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
    length = None       # 3-7
    stress = False      # (True, False) "."
    def __repr__(self):
        if (self.length == None):
            length = ""
        else:
            length = self.length
        if (self.stress):
            stress = "."
        else:
            stress = ""
        if (self.position == 0):
            position = ""
        else:
            position = str(self.position)
        return self.consonant + position + self.vowel + length + stress


def heb2latComp(text):
    for k,v in consonants.items():
        text = text.replace(k,v)
    # shin sin and without dot has to be treated separately because of the order of iterating the alephbet list
    text = text.replace("ש", "sh")

    return text

def heb2lat(text):
    text = unicodedata.normalize("NFKD", text)
    # iterate through text
    g = None
    for c in text:
        #  find placeholder Kringel replace by "_"
        name = unicodedata.name(c).split(" ")
        category = unicodedata.category(c)
        if category != 'Mn':
            if (g != None):
                print (g)
            g = glyph()
        if (name[0] == "HEBREW"):
            #  replace letter according to alephbet, caution for shin
            #   check if sofit letter add 9, else 0
            # get punctuation
            #  if no punctuation write "-"
            #  find punctuation
            if (name[1] == "LETTER"):
                print(unicodedata.category(c), unicodedata.name(c),  end="\n")
                if c in consonants:
                    g.consonant = consonants[c]
                if (name[2] == "FINAL"):
                    g.position = 9
            elif (name[1] == "POINT"):
                print(unicodedata.category(c), unicodedata.name(c),  end="\n")
                if c in vowel:
                    g.vowel = vowel[c]
                elif c == "\u05bc":
                    g.position = 8
    print (g)

    #for k,v in consonants.items():
    #    text = text.replace(k,v)
    # shin sin and without dot has to be treated separately because of the order of iterating the alephbet list
    # text = text.replace("ש", "sh")

    return text


heb2lat("hallo äöü ÄÖÜ HALLO לכד אָכּלֻץ אָאּגּהּ ְ ◌ שׁ שׂ ש");
