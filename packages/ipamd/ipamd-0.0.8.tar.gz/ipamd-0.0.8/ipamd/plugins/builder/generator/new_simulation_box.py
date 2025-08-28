from ipamd.public.models.md_common import Box
configure = {
    "schema": 'io',
    "apply": ["ff"]
}
def func(x, y, z, ff, working_dir):
    return Box(x, y, z, ff, working_dir).new_frame()