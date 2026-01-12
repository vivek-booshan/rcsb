import random

MIYATA_DISSIMILARITY_MAP = {
    "Y": "G",
    "W": "G",
    "K": "G",
    "R": "G",

    "V": "D",
    "L": "D",
    "I": "D",
    "M": "D",
    "F": "D",

    "A": "W",
    "G": "W",
    "P": "W",
    "H": "W",
    "D": "W",
    "E": "W",
    "C": "W",
    "N": "W",
    "Q": "W",
    "T": "W",
    "S": "W",
}


def _generate_random_fasta(length: int, seed: int = 0, header: str = "random_seq"):
    AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
    random.seed(seed)
    seq = "".join(random.choice(AMINO_ACIDS) for _ in range(length))
    return seq


def _mutate_sequence(seq, bsp, seed: int = 67, poly: str = "A"):
    # substitute binding site w/ glycine (Removing interacting residues)
    seq_gly = "".join("G" if i in bsp else res for i, res in enumerate(seq))

    # substitute binding site w/ phenylalanine (packing w/ bulky hydrophobes)
    seq_phe = "".join("F" if i in bsp else res for i, res in enumerate(seq))

    # substitute binding site w/ dissimilar residues (favorable -> unfavorable interactions)
    seq_dis = "".join(
        MIYATA_DISSIMILARITY_MAP[res] if i in bsp else res for i, res in enumerate(seq)
    )

    # random sequence of same length, with fixed seed
    seq_rnd = _generate_random_fasta(len(seq), seed=seed)

    # sequence of alanine of same length
    seq_poly = poly * len(seq)

    mutants = {
        "REF": seq,
        "GLY": seq_gly,
        "PHE": seq_phe,
        "DIS": seq_dis,
        "RND": seq_rnd,
        poly * 3: seq_poly,
    }
    return mutants

    
def mutate_entry(entry, ligand: str = None, positions: tuple[int] = None, seed: int=67, poly='A', inplace: bool = False):
    if positions is not None and ligand is not None:
        raise ValueError("Must specify either 'ligand' or 'positions' only.")

    if positions is not None:
        bsp = positions
        entry.binding_site_positions = bsp
    else:
        if ligand is None and entry.ligand is not None:
            ligand = entry.ligand
        elif (ligand is not None and (f"ligand {ligand.upper()}" in entry.binding_site_positions.keys())):
            entry.ligand = ligand.upper()
        else:
            raise ValueError(f"ligand {ligand.upper()} not valid key.\nValid keys are {entry.binding_site_positions.keys()}")
        bsp = entry.binding_site_positions[f"ligand {ligand.upper()}"]

    mutants =_mutate_sequence(entry.seq, bsp, seed, poly)
    if inplace:
        entry.mutants = mutants
        return


