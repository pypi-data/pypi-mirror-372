from ipamd.public.utils.output import *
from ipamd.public.md_common import AnalysisResult
configure = {
    "schema": 'full'
}
def func(slf, precision=3):
    match slf.type:
        case AnalysisResult.Type.SCALAR:
            prompt(f'{slf.data:.{precision}f}')
        case AnalysisResult.Type.VECTOR:
            for x in slf.data.keys():
                prompt(f'{x}: {slf.data[x]:.{precision}f}')
        case AnalysisResult.Type.DISTRIBUTION:
            for group in slf.data.keys():
                data = slf.data[group]
                prompt(f'{group}: [' + ', '.join([f'{x:.{precision}f}' for x in data]) + ']')
        case AnalysisResult.Type.MATRIX:
            for x in slf.data.keys():
                row = slf.data[x]
                prompt(f'[' + ', '.join([f'{row[y]:.{precision}f}' for y in row.keys()]) + ']')