import os.path
from ipamd.public.utils.output import warning
import numpy as np
from Bio.PDB import Structure, Model, Chain, Residue, Atom, PDBIO
from Bio.SeqUtils import seq3
configure = {
    'type': 'function',
    "schema": 'frame',
    "apply": ['persistency_dir']
}

def func(filename, persistency_dir, frame, ignoring_pbc = True, atom_type_override=''):
    prop = frame.properties(ignoring_image=ignoring_pbc)
    molecules = prop['molecules']

    structure = Structure.Structure("structure")
    model = Model.Model(0)
    structure.add(model)

    n_total = 0
    for i_molecule, molecule in enumerate(molecules):
        if i_molecule >= 26:
            warning('Chain number exceeds the limit of pdb file. Use cif instead.')
            break
        chain = Chain.Chain(chr(65 + i_molecule % 26))
        model.add(chain)
        for i, type_ in enumerate(molecule['type']):
            residue = Residue.Residue((' ', i + 1, ' '), seq3(type_).upper(), ' ')
            atom_type = type_ if atom_type_override == '' else atom_type_override
            atom = Atom.Atom(
                name=atom_type,
                coord=np.multiply(molecule['position'][i], 10),
                bfactor=0.0,
                occupancy=1.0,
                altloc=' ',
                fullname=atom_type,
                element='C',
                serial_number=i + 1 + n_total,
            )
            residue.add(atom)
            chain.add(residue)
        n_total += len(molecule['type'])
    io = PDBIO()
    io.set_structure(structure)
    pdb_filename = os.path.join(persistency_dir, filename + '.pdb')
    io.save(pdb_filename)