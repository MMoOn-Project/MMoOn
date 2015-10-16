#!/usr/bin/python3


import string

alephbetOne = {
    "א": "a",   # e
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "ה": "h",   # ch
    "ו": "w",
    "ז": "z",
    "ח": "x",  # h     x
    "ט": "t",   # th
    "י": "y",
    "כ": "k",
    "ך": "k",
    "ל": "l",
    "מ": "m",
    "ם": "m",
    "נ": "n",
    "ן": "n",
    "ס": "s",   # sz
    "ע": "e",   # a
    "פ": "p",
    "ף": "p",
    "צ": "c",  #       c
    "ץ": "c",  #       c
    "ק": "q",
    "ר": "r",
    "שׁ": "v", #       v
    "שׂ": "u",  # s    u
    "ש": "v",  #       v
    "ת": "f"   # t     f
}

alephbetTwo = {
    "א": "a",   # e
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "ה": "h",   # ch
    "ו": "w",
    "ז": "z",
    "ח": "ch",  # h     x
    "ט": "t",   # th
    "י": "y",
    "כ": "k",
    "ך": "k",
    "ל": "l",
    "מ": "m",
    "ם": "m",
    "נ": "n",
    "ן": "n",
    "ס": "s",   # sz
    "ע": "e",   # a
    "פ": "p",
    "ף": "p",
    "צ": "ts",  #       c
    "ץ": "ts",  #       c
    "ק": "q",
    "ר": "r",
    "שׁ": "sh", #       v
    "שׂ": "sz",  # s    u
    #"ש": "sh",  #       v
    "ת": "th"   # t     f
}
#"ש": "sh",  #       v


def heb2lat(text, singleLetters=False):
    if (singleLetters):
        alephbet = alephbetOne
    else:
        alephbet = alephbetTwo
    for k,v in alephbet.items():
        text = text.replace(k,v)
    # shin sin and without dot has to be treated separately because of the order of iterating the alephbet list
    text = text.replace("ש", "sh")

    return text
