# Author Yechen Qiao
# Common Molecule Utilities for Molecule Transfers with Sapio

from rdkit import Chem
from rdkit.Chem import Crippen, MolToInchi
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.EnumerateStereoisomers import StereoEnumerationOptions, EnumerateStereoisomers
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.SaltRemover import SaltRemover
from rdkit.Chem.rdchem import Mol

from sapiopycommons.chem.IndigoMolecules import indigo, renderer, indigo_inchi

metal_disconnector = rdMolStandardize.MetalDisconnector()
tautomer_params = Chem.MolStandardize.rdMolStandardize.CleanupParameters()
tautomer_params.tautomerRemoveSp3Stereo = False
tautomer_params.tautomerRemoveBondStereo = False
tautomer_params.tautomerReassignStereo = False
tautomer_params.tautomerRemoveIsotopicHs = True
enumerator = rdMolStandardize.TautomerEnumerator(tautomer_params)

def neutralize_atoms(mol) -> Mol:
    """
    Neutralize atoms per https://baoilleach.blogspot.com/2019/12/no-charge-simple-approach-to.html
    """
    pattern = Chem.MolFromSmarts("[+1!h0!$([*]~[-1,-2,-3,-4]),-1!$([*]~[+1,+2,+3,+4])]")
    at_matches = mol.GetSubstructMatches(pattern)
    at_matches_list = [y[0] for y in at_matches]
    if len(at_matches_list) > 0:
        for at_idx in at_matches_list:
            atom = mol.GetAtomWithIdx(at_idx)
            chg = atom.GetFormalCharge()
            hcount = atom.GetTotalNumHs()
            atom.SetFormalCharge(0)
            atom.SetNumExplicitHs(hcount - chg)
            atom.UpdatePropertyCache()
    return mol


def find_all_possible_stereoisomers(m: Mol, only_unassigned=True, try_embedding=True, unique=True, max_isomers=200) \
        -> list[Mol]:
    """
    Find all possible candidates of stereoisomers given the current molecule.

    :param m: The molecule to search for.
    :param only_unassigned: Whether to only permute on unspecified stereocenter.
    :param try_embedding: if set the process attempts to generate a standard RDKit distance geometry conformation for
    the stereisomer.
    If this fails, we assume that the stereoisomer is non-physical and don't return it.
    :param unique: whether to remove duplicates by isomer identity.
    :param max_isomers: Maximum number of search results to return.
    """
    # noinspection PyBroadException
    try:
        opts = StereoEnumerationOptions(tryEmbedding=try_embedding, unique=unique, onlyUnassigned=only_unassigned,
                                        maxIsomers=max_isomers)
        return list(EnumerateStereoisomers(m, options=opts))
    except:
        return []


def has_chiral_centers(m: Mol):
    """
    Returns true iff the molecule provided has at least 1 chiral centers (when stereochemistry is relevant).

    :param m: The molecule to test.
    """
    # noinspection PyBroadException
    try:
        chiral_centers: list = Chem.FindMolChiralCenters(m, force=True, includeUnassigned=True,
                                                         useLegacyImplementation=False)
        return len(chiral_centers) > 0
    except:
        return False


def mol_to_img(mol_str: str) -> str:
    """
    Convert molecule into image.

    :param mol_str: The molecule INCHI.
    :return: The SVG image text.
    """
    mol = indigo.loadMolecule(mol_str)
    return renderer.renderToString(mol)



def mol_to_sapio_partial_pojo(mol: Mol):
    """
    Get the minimum information about molecule to Sapio, just its SMILES, V3000, and image data.

    :param mol: The molecule to read the simplified data from.
    """
    Chem.SanitizeMol(mol)
    mol.UpdatePropertyCache()
    smiles = Chem.MolToSmiles(mol)
    molBlock = Chem.MolToMolBlock(mol)
    img = mol_to_img(mol)
    molecule = dict()
    molecule["smiles"] = smiles
    molecule["molBlock"] = molBlock
    molecule["image"] = img
    return molecule


def mol_to_sapio_substance(mol: Mol, include_stereoisomers: bool = False,
                           normalize: bool = False, remove_salt: bool = False, make_images: bool = False,
                           salt_def: str | None = None, canonical_tautomer: bool = True):
    """
    Convert a molecule in RDKit to a molecule POJO in Sapio.

    :param mol: The molecule in RDKit.
    :param include_stereoisomers: If true, will compute all stereoisomer permutations of this molecule.
    :param normalize If true, will normalize the functional groups and return normalized result.
    :param remove_salt If true, we will remove salts iteratively from the molecule before returning their data.
    We will also populate desaltedList with molecules we deleted.
    :param salt_def: if not none, specifies custom salt to be used during the desalt process.
    :param canonical_tautomer: if True, we will attempt to compute canonical tautomer for the molecule. Slow!
    This is needed for a registry. Note it stops after enumeration of 1000.
    :return: The molecule POJO for Sapio.
    """
    molecule = dict()
    Chem.SanitizeMol(mol)
    mol.UpdatePropertyCache()
    Chem.GetSymmSSSR(mol)
    if normalize:
        try:
            mol = Chem.RemoveHs(mol)
            mol = metal_disconnector.Disconnect(mol)
            mol = rdMolStandardize.Normalize(mol)
            molecule["normError"] = ""
        except Exception as e:
            molecule["normError"] = str(e)
    if remove_salt:
        try:
            remover = SaltRemover(defnData=salt_def)
            mol, deleted = remover.StripMolWithDeleted(mol)
            molecule["desaltedList"] = [Chem.MolToSmarts(x) for x in deleted]
            molecule["desaltError"] = ""
        except Exception as e:
            molecule["desaltError"] = str(e)
            molecule["desaltedList"] = []
    if normalize or remove_salt:
        mol = neutralize_atoms(mol)
    #//CR-46021 Jarvis: no canonicalize tautomers.
    if canonical_tautomer:
        mol = enumerator.Canonicalize(mol)
    Chem.SanitizeMol(mol)
    mol.UpdatePropertyCache()
    Chem.GetSymmSSSR(mol)
    smiles = Chem.MolToSmiles(mol)
    cLogP = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    amw = Descriptors.MolWt(mol)
    exactMass = Descriptors.ExactMolWt(mol)
    molFormula = rdMolDescriptors.CalcMolFormula(mol)
    charge = Chem.GetFormalCharge(mol)
    molBlock = Chem.MolToMolBlock(mol)

    molecule["cLogP"] = cLogP
    molecule["tpsa"] = tpsa
    molecule["amw"] = amw
    molecule["exactMass"] = exactMass
    molecule["molFormula"] = molFormula
    molecule["charge"] = charge
    molecule["numHBondAcceptors"] = rdMolDescriptors.CalcNumHBA(mol)
    # This is number of H-Bond Donor
    molecule["numHBonds"] = rdMolDescriptors.CalcNumHBD(mol)
    molecule["molBlock"] = molBlock
    rdkit_inchi = MolToInchi(mol)
    # If INCHI is completely invalid, we fail this molecule.
    if not rdkit_inchi:
        MolToInchi(mol, treatWarningAsError=True)
    if make_images:
        img = mol_to_img(smiles)
        molecule["image"] = img
    else:
        molecule["image"] = None
    # We need to test the INCHI can be loaded back to indigo.
    indigo_mol = indigo.loadMolecule(molBlock)
    indigo_mol.aromatize()
    indigo_inchi.resetOptions()
    indigo_inchi_str = indigo_inchi.getInchi(indigo_mol)
    molecule["inchi"] = indigo_inchi_str
    indigo_inchi_key_str = indigo_inchi.getInchiKey(indigo_inchi_str)
    molecule["inchiKey"] = indigo_inchi_key_str
    molecule["smiles"] = indigo_mol.smiles()

    if include_stereoisomers and has_chiral_centers(mol):
        stereoisomers = find_all_possible_stereoisomers(mol, only_unassigned=False, try_embedding=False, unique=True)
        molecule["stereoisomers"] = [mol_to_sapio_partial_pojo(x) for x in stereoisomers]
    return molecule


def mol_to_sapio_compound(mol: Mol, include_stereoisomers: bool = False,
                          salt_def: str | None = None, resolve_canonical: bool = True,
                          make_images: bool = False, canonical_tautomer: bool = True):
    ret = dict()
    ret['originalMol'] = mol_to_sapio_substance(mol, include_stereoisomers,
                                                normalize=False, remove_salt=False, make_images=make_images,
                                                canonical_tautomer=canonical_tautomer)
    if resolve_canonical:
        ret['canonicalMol'] = mol_to_sapio_substance(mol, include_stereoisomers=False,
                                                     normalize=True, remove_salt=True, make_images=make_images,
                                                     salt_def=salt_def, canonical_tautomer=canonical_tautomer)
    return ret
