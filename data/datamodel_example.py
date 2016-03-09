#!/usr/bin/python3

import sys
import getopt

import rdflib
from rdflib import OWL
from rdflib import Namespace

import datamodel
from datamodel import Lexeme
from datamodel import Root
from datamodel import Affix
from datamodel import Wordform

def main(args=sys.argv[1:]):
    try:
        opts, args = getopt.getopt(args, "hf:c:r:", ["help", "file=", "csvoutfile=", "rdfoutfile="])
    except getopt.GetoptError as err:
        # print help information and exit:
        LOG.error(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    out_file_rdf = None

    for opt, opt_val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-r", "--rdfoutfile"):
            out_file_rdf = opt_val
        else:
            assert False, "unhandled option"

    mmoon = Namespace("http://mmoon.org/mmoon/")
    mmoon_heb = Namespace("http://mmoon.org/lang/heb/schema/oh/")
    heb_inventory = Namespace("http://mmoon.org/lang/heb/inventory/oh/")

    graph = rdflib.Graph()
    graph.bind("mmoon", mmoon)
    graph.bind("heb_schema", mmoon_heb)
    graph.bind("heb_inventory", heb_inventory)

    lexeme = Lexeme("דִּבֵּר", mmoon_heb.Barkali_piel_1, mmoon_heb.Verb)
    root = Root("דבר")

    # TODO maybe we should use the latin code for the transfixes, because of the dagesh
    # mmoon.ABSINF
    # mmoon.KAFINF
    # mmoon.BETINF
    # …
    affix = Affix("◌ִּ◌ֵּ◌", heb_inventory.ABSINF)
    wordform = Wordform("דְּבֵּר", root, affix)
    lexeme.addWordform(wordform)

    lexeme.toRDF(graph)
    root.toRDF(graph)
    affix.toRDF(graph)
    wordform.toRDF(graph)

    graph.add((heb_inventory.term(""), OWL.imports, mmoon_heb.term("")))
    graph.serialize(out_file_rdf, "turtle")

if __name__ == "__main__":
    main()
