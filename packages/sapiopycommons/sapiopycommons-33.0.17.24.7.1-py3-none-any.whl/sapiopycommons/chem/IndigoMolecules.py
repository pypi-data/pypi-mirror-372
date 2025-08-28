from indigo import Indigo, IndigoObject
from indigo.inchi import IndigoInchi
from indigo.renderer import IndigoRenderer

indigo = Indigo()
renderer = IndigoRenderer(indigo)
indigo.setOption("render-output-format", "svg")
indigo.setOption("ignore-stereochemistry-errors", True)
indigo.setOption("render-stereo-style", "ext")
indigo.setOption("aromaticity-model", "generic")
indigo.setOption("render-coloring", True)
indigo_inchi = IndigoInchi(indigo);


def highlight_mol_substructure(query: IndigoObject, sub_match: IndigoObject):
    """
    Highlight the bonds and atoms for substructure search result.

    :param sub_match: The substructure search match obtained from indigo.substructureMatcher(mol).match(query).
    :param query: The query we were running to match the original structure.
    """
    for qatom in query.iterateAtoms():
        atom = sub_match.mapAtom(qatom)
        if atom is None:
            continue
        atom.highlight()

        for nei in atom.iterateNeighbors():
            if not nei.isPseudoatom() and not nei.isRSite() and nei.atomicNumber() == 1:
                nei.highlight()
                nei.bond().highlight()

    for bond in query.iterateBonds():
        bond = sub_match.mapBond(bond)
        if bond is None:
            continue
        bond.highlight()


def highlight_reactions(query_reaction_smarts: IndigoObject, reaction_match: IndigoObject):
    """
    Highlight the bonds and atoms for substructure search result of reaction that's in the query and survived the mapping.

    :param query_reaction_smarts: The query we ran substructure search on.
    :param reaction_match: The substructure search match obtained from indigo.substructureMatcher(reaction).match(query).
    :return:
    """
    for q_mol in query_reaction_smarts.iterateMolecules():
        matched_mol = reaction_match.mapMolecule(q_mol)
        sub_match = indigo.substructureMatcher(matched_mol).match(q_mol)
        highlight_mol_substructure(q_mol, sub_match)
