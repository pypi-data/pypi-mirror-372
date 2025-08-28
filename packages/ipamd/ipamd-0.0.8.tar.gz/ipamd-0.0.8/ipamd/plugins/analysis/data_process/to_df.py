import pandas as pd

from ipamd.public.models.md_common import AnalysisResult

configure = {
    "type": 'function',
    "schema": 'full'
}
def func(slf):
    match slf.type:
        case AnalysisResult.Type.SCALAR:
            pass
        case _:
            df = pd.DataFrame(list(slf.data.items()), columns=['Key', 'Value'])
    print(df)
