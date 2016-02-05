#!/usr/bin/python3

import logging
import logging.config
import csv
import sys
import getopt
import string
from heb2lat import heb2lat


# http://mmoon.org/lang/heb/schema/oh/PrimaryRoot
import urllib
import rdflib
from rdflib import RDF
from rdflib import RDFS
from rdflib import OWL
#from rdflib import DC
from rdflib import Namespace
import hashlib
import regex

mmoon = Namespace("http://mmoon.org/mmoon/")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")
gold = Namespace("http://purl.org/linguistics/gold/")
DC = Namespace("http://purl.org/dc/elements/1.1/")


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
LOG = logging.getLogger('mmoon')

def main(args=sys.argv[1:]):
    try:
        opts, args = getopt.getopt(args, "hf:c:r:",
                                   ["help", "file=", "csvoutfile=", "rdfoutfile="])
    except getopt.GetoptError as err:
        # print help information and exit:
        LOG.error(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    file_from_cli = None
    out_file_csv = None
    out_file_rdf = None

    for opt, opt_val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            file_from_cli = opt_val
        elif opt in ("-c", "--csvoutfile"):
            out_file_csv = opt_val
        elif opt in ("-r", "--rdfoutfile"):
            out_file_rdf = opt_val
        else:
            assert False, "unhandled option"


    file_fd = open(file_from_cli, 'r')

    csvReader = csv.DictReader(file_fd)

    forbiddenChars = [" ", "(", ")", "[", "]", "/", "—"]

    lexemeKategorie = [mmoon_heb.CommonNoun, mmoon_heb.Verb, mmoon_heb.Adjective]

    charTranslation = str.maketrans("\"","״")
    removeTranslation = str.maketrans("?!","  ")

    a = 0
    b = 0
    c = 0
    kategorie = set()
    filteredRows = []
    for row in csvReader:
        row['vocalized'] = row['vocalized'].strip()
        row['vocalized'] = row['vocalized'].translate(removeTranslation)
        row['vocalized'] = row['vocalized'].translate(charTranslation)
        row['unvocalized'] = row['unvocalized'].strip()
        row['unvocalized'] = row['unvocalized'].translate(removeTranslation)
        row['unvocalized'] = row['unvocalized'].translate(charTranslation)

        if not row['vocalized'] or any(char in row['vocalized'] for char in forbiddenChars):
            #print("removed because of A")
            a=a+1
        elif not row['unvocalized'] or any(char in row['unvocalized'] for char in forbiddenChars):
            #print("removed because of B")
            b=b+1
        elif not row['Kategorie']:
            #print("removed because of 'Kategorie'")
            c=c+1
        else:
            #print(row)
            kategorie.add(row['Kategorie'])
            row['root'] = normalizeRoot(row['root'])


            row['Genus/Binjan'] = row['Genus/Binjan'].translate(charTranslation)
            row['Genus/Binjan'] = row['Genus/Binjan'].strip()

            row['Kategorie'] = row['Kategorie'].translate(charTranslation)
            row['Kategorie'] = row['Kategorie'].strip()

            row['secundaryRoot'] = normalizeRoot(row['secundaryRoot'])
            filteredRows.append(row)
    file_fd.close()

    # Write Rows to CSV if filename is given
    if (out_file_csv):
        outfile_fd = open(out_file_csv, 'w')

        csvWriter = csv.DictWriter(
            outfile_fd,
            fieldnames=["vocalized","unvocalized","secundaryRoot","root","Genus/Binjan","Kategorie","hebräisch","deutsch","englisch","russisch"],
            # ,"root-de"
            extrasaction="ignore"
        )
        csvWriter.writeheader()
        csvWriter.writerows(filteredRows)
        outfile_fd.close()

    print("a:", str(a), "b:", str(b), "c:", str(c), "rest:", str(len(filteredRows)), "sum:", str(a+b+len(filteredRows)))
    print(kategorie)

    graph = rdflib.Graph()
    graph.bind("mmoon", mmoon)
    graph.bind("heb_schema", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)
    graph.bind("gold", gold)
    graph.bind("owl", OWL)
    graph.bind("dc", DC)

    for row in filteredRows:
        #if row['Kategorie']:
        #    store.add()

        isLexeme = False
        lexeme = None
        roots = []
        wordclassResource = None
        inflectionalCategories = []
        binjan = None
        rdfType = None

        # TODO
        # - wenn Kategorie shoresh ist, dann nur explizit wurzeln anlegen

        if row['Kategorie']:
            # Ignoriere, weil zu unspezifisch oder weil ich es nicht zuordnen kann: "מילים", "מילת הסבר", "מילת קישור",
            # TODO: "מלת חיבור", "מילת חיבור", "מילת קריאה", "מילת שאלה"

            if row['Kategorie'] == "פועל":
                # TODO ist in OpenHebrewInstances.ttl noch als http://mmoon.org/lang/heb/inventory/oh#Verb angegeben
                wordclassResource = mmoon_heb.Verb
                if row['Genus/Binjan'] == "פעל":
                    binjan = mmoon_heb.term("pa%27al")
                elif row['Genus/Binjan'] == "נפעל":
                    binjan = mmoon_heb.term("nif%27al")
                elif row['Genus/Binjan'] == "פיעל":
                    binjan = mmoon_heb.term("pi%27el")
                elif row['Genus/Binjan'] == "פולל" or row['Genus/Binjan'] == "פיעל פולל":
                    binjan = mmoon_heb.term("polel")
                elif row['Genus/Binjan'] == "פיעל (פעלל)":
                    binjan = mmoon_heb.term("pa%27lel")
                elif row['Genus/Binjan'] == "פועל":
                    binjan = mmoon_heb.term("pu%27al")
                elif row['Genus/Binjan'] == "פועל (פועלל)":
                    binjan = mmoon_heb.term("pu%27lel")
                elif row['Genus/Binjan'] == "הפעיל":
                    binjan = mmoon_heb.term("hif%27il")
                elif row['Genus/Binjan'] == "הופעל":
                    binjan = mmoon_heb.term("huf%27al")
                elif row['Genus/Binjan'] == "התפעל":
                    binjan = mmoon_heb.term("hitpa%27el")
            elif row['Kategorie'] == "שם עצם":
                wordclassResource = mmoon_heb.CommonNoun
                if row['Genus/Binjan'] == "ז״ר" or row['Genus/Binjan'] == "זכר רבים":
                    # masc. plur.
                    inflectionalCategories.append(mmoon_heb.Masculine)
                    inflectionalCategories.append(mmoon_heb.Plural)
                elif row['Genus/Binjan'] == "ז״ז":
                    # masc. dual
                    inflectionalCategories.append(mmoon_heb.Masculine)
                    inflectionalCategories.append(mmoon_heb.Dual)
                elif row['Genus/Binjan'] == "זכר":
                    # masc.
                    inflectionalCategories.append(mmoon_heb.Masculine)
                elif row['Genus/Binjan'] == "זו״נ" or row['Genus/Binjan'] == "זכר/נקבה":
                    #  masc. and fem.
                    inflectionalCategories.append(mmoon_heb.Feminine)
                    inflectionalCategories.append(mmoon_heb.Masculine)
                elif row['Genus/Binjan'] == "נ״ר" or row['Genus/Binjan'] == "נקבה רבים":
                    # fem. pl.
                    inflectionalCategories.append(mmoon_heb.Feminine)
                    inflectionalCategories.append(mmoon_heb.Plural)
                elif row['Genus/Binjan'] == "נקבה":
                    # fem.
                    inflectionalCategories.append(mmoon_heb.Feminine)
            elif row['Kategorie'] == "שם תואר":
                wordclassResource = mmoon_heb.Adjective
            elif row['Kategorie'] == "תואר פועל":
                wordclassResource = mmoon_heb.Adverb
            elif row['Kategorie'] == "מילת יחס" or row['Kategorie'] == "מלת יחס":
                wordclassResource = mmoon_heb.Preposition
            elif row['Kategorie'] == "סופית":
                rdfType = mmoon_heb.Suffix
            elif row['Kategorie'] == "מילת יחס":
                true

        if row['vocalized']:
            voc = row['vocalized']
            if any(wordclassResource == kategorie for kategorie in lexemeKategorie):
                isLexeme = True
                lexeme = rdflib.term.URIRef(heb_inventory+"Lexeme_"+voc)
                graph.add((lexeme, RDF.type, mmoon_heb.Lexeme))
            elif rdfType and rdfType == mmoon_heb.Suffix:
                lexeme = rdflib.term.URIRef(heb_inventory+"Suffix_"+voc)
                graph.add((lexeme, RDF.type, rdfType))
            else:
                lexeme = rdflib.term.URIRef(heb_inventory+"Word_"+voc)
                graph.add((lexeme, RDF.type, mmoon.Word))
            vocrep = rdflib.term.URIRef(heb_inventory+"Representation_"+voc)
            vocliteral = rdflib.term.Literal(row['vocalized'], lang="he")

            graph.add((vocrep, RDF.type, mmoon_heb.Representation))
            graph.add((vocrep, mmoon_heb.vocalizedRepresentation, vocliteral))
            if lexeme:
                graph.add((lexeme, RDFS.label, vocliteral))
                graph.add((lexeme, mmoon.hasRepresentation, vocrep))

        if row['unvocalized']:
            unvoc = row['unvocalized']
            unvocrep = rdflib.term.URIRef(heb_inventory+"Representation_"+unvoc)
            unvocliteral = rdflib.term.Literal(row['unvocalized'], lang="he")

            graph.add((unvocrep, RDF.type, mmoon_heb.Representation))
            graph.add((unvocrep, mmoon_heb.unvocalizedRepresentation, unvocliteral))

            if lexeme:
                graph.add((lexeme, mmoon.hasRepresentation, unvocrep))

        if row['deutsch']:
            translation = addTranslation(graph, row['deutsch'], "de")
            if lexeme:
                graph.add((lexeme, gold.translation, translation))

        if row['englisch']:
            translation = addTranslation(graph, row['englisch'], "en")
            if lexeme:
                graph.add((lexeme, gold.translation, translation))

        if row['russisch']:
            translation = addTranslation(graph, row['russisch'], "ru")
            if lexeme:
                graph.add((lexeme, gold.translation, translation))

        if row['root'] or row['secundaryRoot']:
            # secondary-root -> secondary-root
            # root -> primary-root
            # nur eins von beiden -> root
            if (row['root'] == row['secundaryRoot'] or not row['root'] or not row['secundaryRoot']):
                root = row['secundaryRoot']
                if not root:
                    root = row['root']
                rootResource = addRootResource(graph, root, mmoon_heb.PrimaryRoot)
                roots.append(rootResource)
            else :
                #rootResourceA = addRootResource(graph, row['root'], mmoon_heb.PrimaryRoot)
                rootResource = addRootResource(graph, row['secundaryRoot'], mmoon_heb.SecondaryRoot, row['root'])
                roots.append(rootResource)

        #######

        if lexeme:
            if wordclassResource:
                graph.add((lexeme, mmoon.hasWordclassAffiliation, wordclassResource))
            for inflectionalCategory in inflectionalCategories :
                graph.add((lexeme, mmoon.hasInflectionalCategory, inflectionalCategory))
            if binjan:
                graph.add((lexeme, mmoon.consistsOfMorph, binjan))

            for root in roots :
                graph.add((lexeme, mmoon_heb.consistsOfMorph, root))
                if isLexeme:
                    graph.add((root, mmoon_heb.belongsToLexeme, lexeme))
                else:
                    graph.add((root, mmoon.belongsToWord, lexeme))

    graph.add((heb_inventory.term(""), OWL.imports, mmoon_heb.term("")))
    graph.serialize(out_file_rdf, "turtle")

def addTranslation(graph, translationStr, language):
    translationStr = translationStr.strip()
    translationStrQuoted = urllib.parse.quote(translationStr)

    translation = rdflib.term.URIRef(heb_inventory+"Representation/" + language + "/"+translationStrQuoted)

    graph.add((translation, RDF.type, mmoon.Representation))
    graph.add((translation, mmoon.orthographicRepresentation, rdflib.term.Literal(translationStr, lang=language)))
    graph.add((translation, DC.language, rdflib.term.Literal(language)))
    return translation

def addRootResource(graph, root, classResource, primaryRoot=None):
    # https://stackoverflow.com/questions/33068727/how-to-split-unicode-strings-character-by-character-in-python
    #rootDashed = "-".join(regex.findall('\p{L}\p{M}*', root))
    rootDashed = "-".join(regex.findall('\X', root))

    rootResource = rdflib.term.URIRef(heb_inventory+"root_"+root)
    #rootResource = rdflib.term.URIRef(heb_inventory+"root_"+heb2lat(rootDashed))
    rootliteral = rdflib.term.Literal(root, lang="he")

    graph.add((rootResource, RDF.type, classResource))
    graph.add((rootResource, RDF.type, mmoon_heb.Root))
    graph.add((rootResource, RDFS.label, rootliteral))

    if primaryRoot:
        primaryRootResource = addRootResource(graph, primaryRoot, mmoon_heb.PrimaryRoot)
        graph.add((rootResource, mmoon_heb.consistsOfRoot, primaryRootResource))

    return rootResource

def normalizeRoot(root):

    forbiddenChars = ["(", ")", "[", "]", "/"]
    root = root.strip()

    if not root or root == "—" or root == "—" or any(char in root for char in forbiddenChars):
        return ""

    return root.replace(" ", "").replace("-", "")


if __name__ == "__main__":
    main()
