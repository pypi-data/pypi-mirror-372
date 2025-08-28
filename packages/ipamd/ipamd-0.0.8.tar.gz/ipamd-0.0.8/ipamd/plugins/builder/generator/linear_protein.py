from ipamd.public.models.md_common import Molecule, Atom
configure = {
    "apply": ['ff']
}
def func(protein_name, sequence, ff):
    molecule = Molecule(protein_name, cg='CA')
    length = len(sequence)
    z = 0
    for index, r in enumerate(sequence):
        if index == 0:
            custom_mass = f'compute:{ff.atom_definition[r]["mass"]}+1.008'
        elif index == length - 1:
            custom_mass = f'compute:{ff.atom_definition[r]["mass"]}+17.007'
        else:
            custom_mass = None
        molecule.add_atom(
            Atom(
                velocity=(0, 0, 0),
                atom_type=r,
                mass=custom_mass,
                ff=ff
            ),
            coordinate=(0, 0, z),
            bond='B-B'
        )
        z += 0.38
    return molecule