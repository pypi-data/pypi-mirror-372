def func(molecule):
    for i in range(len(molecule.atoms)):
        atom = molecule.atoms[i]
        if atom['rigid_body'] == True:
            molecule.atoms[i]['prototype'] = 'RIGID'

    return molecule