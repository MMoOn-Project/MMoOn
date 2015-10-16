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

        if row['vocalized']:
            # urllib.parse.urlencode()
            voc = hashlib.md5(row['vocalized'].encode('utf-8')).hexdigest()
            voclexeme = rdflib.term.URIRef(heb_inventory+"lexeme_"+voc)
            vocliteral = rdflib.term.Literal(row['vocalized'], lang="he")

            graph.add((voclexeme, RDF.type, mmoon_heb.Lexeme))
            graph.add((voclexeme, RDFS.label, vocliteral))

        if row['unvocalized']:
            # urllib.parse.urlencode()
            unvoc = hashlib.md5(row['unvocalized'].encode('utf-8')).hexdigest()
            unvoclexeme = rdflib.term.URIRef(heb_inventory+"lexeme_"+unvoc)
            unvocliteral = rdflib.term.Literal(row['unvocalized'], lang="he")

            graph.add((unvoclexeme, RDF.type, mmoon_heb.Lexeme))
            graph.add((unvoclexeme, RDFS.label, unvocliteral))

        if row['root'] or row['secundaryRoot']:
            #print (row['root'], "->", heb2lat(row['root']))
            # secondary-root -> secondary-root
            # root -> primary-root
            # nur eins von beiden -> root
            if (row['root'] == row['secundaryRoot'] or not row['root'] or not row['secundaryRoot']):
                root = row['secundaryRoot']
                if not root:
                    root = row['root']

                addRootResource(graph, root, mmoon_heb.Root)
            else :
                addRootResource(graph, row['root'], mmoon_heb.PrimaryRoot)
                addRootResource(graph, row['secundaryRoot'], mmoon_heb.SecondaryRoot)

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

def normalizeRoot(root):

    forbiddenChars = ["(", ")", "[", "]", "/"]
    root = root.strip()

    if not root or root == "—" or root == "—" or any(char in root for char in forbiddenChars):
        return ""

    return root.replace(" ", "").replace("-", "")


if __name__ == "__main__":
    main()
