from ipamd.public.models.md_common import AnalysisResult
configure = {
    "schema": 'full'
}
def func(slf, action='average', new_name=None):
    result = AnalysisResult(
        title=slf.title + '-flatten' if new_name is None else new_name,
        type=AnalysisResult.Type.UNKNOWN,
        data={}
    )
    match (slf.type, action):
        case (AnalysisResult.Type.SCALAR, 'average') | (AnalysisResult.Type.SCALAR, 'sum'):
            result.type = AnalysisResult.Type.SCALAR
            result.data = slf.data
        case (AnalysisResult.Type.VECTOR, 'average'):
            result.type = AnalysisResult.Type.SCALAR
            averaged_value = 0
            for value in slf.data.values():
                averaged_value += value
            result.data = averaged_value / len(slf.data)
        case (AnalysisResult.Type.VECTOR, 'sum'):
            pass
        case (AnalysisResult.Type.MATRIX, 'average'):
            pass
        case (AnalysisResult.Type.MATRIX, 'sum'):
            pass
    return result