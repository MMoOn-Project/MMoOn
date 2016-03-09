#!/usr/bin/python3

import sys
import getopt

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

    lexeme = Lexeme("דִּבֵּר", datamodel.schema.Barkali_piel_1, datamodel.schema.Verb)
    root = Root("דבר")

    # TODO maybe we should use the latin code for the transfixes, because of the dagesh
    # mmoon.ABSINF
    # mmoon.KAFINF
    # mmoon.BETINF
    # …
    affix = Affix("◌ִּ◌ֵּ◌", datamodel.inventory.ABSINF)
    wordform = Wordform("דְּבֵּר", root, affix)
    lexeme.addWordform(wordform)

    graph = datamodel.getNewGraph()

    lexeme.toRDF(graph)
    root.toRDF(graph)
    affix.toRDF(graph)
    wordform.toRDF(graph)

    datamodel.writeGraphToFile(graph, out_file_rdf)

if __name__ == "__main__":
    main()
