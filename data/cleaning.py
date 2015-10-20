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
from rdflib import Namespace
import hashlib
import regex

mmoon = Namespace("http://mmoon.org/mmoon#")
mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh#")


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

    charTranslation = str.maketrans("\"","״")

    a = 0
    b = 0
    c = 0
    kategorie = set()
    filteredRows = []
    for row in csvReader:
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
            if row['vocalized'] == "???":
                row['vocalized'] = ""
            row['vocalized'] = row['vocalized'].translate(charTranslation)
            row['unvocalized'] = row['unvocalized'].translate(charTranslation)
            row['Genus/Binjan'] = row['Genus/Binjan'].translate(charTranslation)
            row['Kategorie'] = row['Kategorie'].translate(charTranslation)
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
    graph.bind("mmoon_heb", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)

    for row in filteredRows:
        #if row['Kategorie']:
        #    store.add()

        lexemes = []
        roots = []

        # TODO
        # - Genus/Binjan
        # - Kategorie
        # - Übersetzungen

        # http://mmoon.org/lang/heb/schema/oh/OrthographicRepresentation
        if row['vocalized']:
            # urllib.parse.urlencode()
            #voc = hashlib.md5(row['vocalized'].encode('utf-8')).hexdigest()
            voc = row['vocalized']
            voclexeme = rdflib.term.URIRef(heb_inventory+"lexeme_"+voc)
            vocliteral = rdflib.term.Literal(row['vocalized'], lang="he")

            graph.add((voclexeme, RDF.type, mmoon_heb.OrthographicRepresentation))
            graph.add((voclexeme, RDF.type, mmoon_heb.Lexeme))
            graph.add((voclexeme, RDFS.label, vocliteral))
            lexemes.append(voclexeme)

        if row['unvocalized']:
            # urllib.parse.urlencode()
            #unvoc = hashlib.md5(row['unvocalized'].encode('utf-8')).hexdigest()
            unvoc = row['unvocalized']
            unvoclexeme = rdflib.term.URIRef(heb_inventory+"lexeme_"+unvoc)
            unvocliteral = rdflib.term.Literal(row['unvocalized'], lang="he")

            graph.add((unvoclexeme, RDF.type, mmoon_heb.OrthographicRepresentation))
            graph.add((unvoclexeme, RDF.type, mmoon_heb.Lexeme))
            graph.add((unvoclexeme, RDFS.label, unvocliteral))
            lexemes.append(unvoclexeme)

        if row['root'] or row['secundaryRoot']:
            # secondary-root -> secondary-root
            # root -> primary-root
            # nur eins von beiden -> root
            if (row['root'] == row['secundaryRoot'] or not row['root'] or not row['secundaryRoot']):
                root = row['secundaryRoot']
                if not root:
                    root = row['root']
                rootResource = addRootResource(graph, root, mmoon_heb.Root)
                roots.append(rootResource)
            else :
                rootResourceA = addRootResource(graph, row['root'], mmoon_heb.PrimaryRoot)
                rootResourceB = addRootResource(graph, row['secundaryRoot'], mmoon_heb.SecondaryRoot)
                roots.append(rootResourceA)
                roots.append(rootResourceB)

        if row['Kategorie']:
            # Ignoriere, weil zu unspezifisch oder weil ich es nicht zuordnen kann: "מילים", "מילת הסבר", "מילת קישור",
            # TODO: "מלת חיבור", "מילת חיבור", "מילת קריאה", "מילת שאלה"
            classResource = None
            inflectionalCategories = []

            if row['Kategorie'] == "פועל":
                # TODO ist in OpenHebrewInstances.ttl noch als http://mmoon.org/lang/heb/inventory/oh#Verb angegeben
                classResource = mmoon_heb.Verb
                if row['Genus/Binjan'] == "ז״ר" or row['Genus/Binjan'] == "ז\"ר" or row['Genus/Binjan'] == "זכר רבים":
                    # masc. plur.
                    inflectionalCategories.append(mmoon_heb.Masculine)
                    inflectionalCategories.append(mmoon_heb.Plural)
            elif row['Kategorie'] == "שם עצם":
                classResource = mmoon_heb.Noun
                if row['Genus/Binjan'] == "ז״ר" or row['Genus/Binjan'] == "ז\"ר" or row['Genus/Binjan'] == "זכר רבים":
                    # masc. plur.
                    inflectionalCategories.append(mmoon_heb.Masculine)
                    inflectionalCategories.append(mmoon_heb.Plural)
                elif row['Genus/Binjan'] == "ז״ז":
                    # masc. dual
                    inflectionalCategories.append(mmoon_heb.Masculine)
                    # TODO Dual
                elif row['Genus/Binjan'] == "זכר":
                    # masc.
                    inflectionalCategories.append(mmoon_heb.Masculine)
                elif row['Genus/Binjan'] == "זו\"נ" or row['Genus/Binjan'] == "זו״נ" or row['Genus/Binjan'] == "זכר/נקבה":
                    #  masc. and fem.
                    inflectionalCategories.append(mmoon_heb.Feminine)
                    inflectionalCategories.append(mmoon_heb.Masculine)
                elif row['Genus/Binjan'] == "נ״ר" or row['Genus/Binjan'] == "נקבה רבים":
                    # fem. pl.
                    inflectionalCategories.append(mmoon_heb.Feminine)
                    inflectionalCategories.append(mmoon_heb.Plural)
                elif row['Genus/Binjan'] == "נקבה":
                    # fem
                    inflectionalCategories.append(mmoon_heb.Feminine)
            elif row['Kategorie'] == "שם תואר":
                classResource = mmoon_heb.Adjectiv
            elif row['Kategorie'] == "תואר פועל":
                classResource = mmoon_heb.Adverb
            elif row['Kategorie'] == "מילת יחס" or row['Kategorie'] == "מלת יחס":
                classResource = mmoon_heb.Preposition
            elif row['Kategorie'] == "מילת יחס":
                true



            if classResource:
                for lexeme in lexemes :
                    graph.add((lexeme, RDF.type, classResource))
            if inflectionalCategories:
                for lexeme in lexemes :
                    for inflectionalCategory in inflectionalCategories :
                        graph.add((lexeme, mmoon.hasInflectionalCategory, inflectionalCategory))



        for lexeme in lexemes :
            for root in roots :
                graph.add((lexeme, mmoon_heb.consistsOfMorph, root))
                graph.add((root, mmoon_heb.belongsToWord, lexeme))


    graph.serialize(out_file_rdf, "turtle")

def addRootResource(graph, root, classResource):
    # https://stackoverflow.com/questions/33068727/how-to-split-unicode-strings-character-by-character-in-python
    #rootDashed = "-".join(regex.findall('\p{L}\p{M}*', root))
    rootDashed = "-".join(regex.findall('\X', root))

    rootResourceHeb = rdflib.term.URIRef(heb_inventory+"root_"+root)
    rootResource = rdflib.term.URIRef(heb_inventory+"root_"+heb2lat(rootDashed))
    rootliteral = rdflib.term.Literal(root, lang="he")

    graph.add((rootResourceHeb, RDF.type, classResource))
    graph.add((rootResourceHeb, OWL.sameAs, rootResource))
    graph.add((rootResourceHeb, RDFS.seeAlso, rootResource))

    graph.add((rootResource, RDF.type, classResource))
    graph.add((rootResource, RDFS.label, rootliteral))

    return rootResource

def normalizeRoot(root):

    forbiddenChars = ["(", ")", "[", "]", "/"]
    root = root.strip()

    if not root or root == "—" or root == "—" or any(char in root for char in forbiddenChars):
        return ""

    return root.replace(" ", "").replace("-", "")


if __name__ == "__main__":
    main()
