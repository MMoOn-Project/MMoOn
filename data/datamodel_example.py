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

    # TODO maybe we should use the latin code for the strings especially the  transfixes, because of the dagesh issue
    #
    # Lexeme takes the binjan as second argument:
    #   e.g. datamodel.schema.Barkali_piel_1
    # The third argument is the word class:
    #   e.g. datamodel.schema.Verb
    # For th affix/transfix its relation to a morpheme has to be specified:
    #   e.g. mmoon.ABSINF, mmoon.KAFINF, or mmoon.BETINF, …
    # The wordform has to be provided with the relations to the root and the affix it consists of

    lexeme = Lexeme("D8iB8eR-", datamodel.schema.Barkali_piel_1, datamodel.schema.Verb)   # "דִּבֵּר"
    root = Root("D-B-R-")   # "דבר"

    affix_1 = Affix("_8i_8e_-", datamodel.inventory.term("3_SG_M"))    # "◌ִּ◌ֵּ◌"  # TODO stimmt 3_SG_M ?
    wordform_1 = Wordform("D8iB8eR-", root, affix_1)    # "דְּבֵּר"
    lexeme.addWordform(wordform_1)

    affix_2 = Affix("_8a_8e_-", datamodel.inventory.term("ABSINF"))
    wordform_2 = Wordform("D8aB8eR-", root, affix_2)
    lexeme.addWordform(wordform_2)

    # "_8i_8m_-H-"
    # "_i_8m_-H-"
    affix_3 = Affix("_8i_8m_tH-", datamodel.inventory.term("3_SG_F_PST"))
    wordform_3 = Wordform("D8iB8mRtH-", root, affix_3)
    lexeme.addWordform(wordform_3)

    graph = datamodel.getNewGraph()

    lexeme.toRDF(graph)
    root.toRDF(graph)
    affix_1.toRDF(graph)
    wordform_1.toRDF(graph)
    affix_2.toRDF(graph)
    wordform_2.toRDF(graph)
    affix_3.toRDF(graph)
    wordform_3.toRDF(graph)

    datamodel.writeGraphToFile(graph, out_file_rdf)

if __name__ == "__main__":
    main()
