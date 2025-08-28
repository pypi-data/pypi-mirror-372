import requests
from ipamd.public.utils.output import *
configure = {
    "schema": 'io',
}
def func(arg1, working_dir):
    url = "https://files.rcsb.org/download/" + arg1 + ".pdb"
    data = requests.get(url)
    with open(working_dir + '/' + arg1 + '.pdb', 'wb') as f:
        f.write(data.content)
    info('Downloaded ' + arg1 + ' from RCSB.')