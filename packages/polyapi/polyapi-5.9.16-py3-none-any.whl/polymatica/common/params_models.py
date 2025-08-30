from typing import List, Optional, Union

from pydantic import BaseModel, StrictBool, StrictInt, StrictStr


class SetMeasuresParams(BaseModel):
    measure_names: List[StrictStr]
    measure_formats: List[dict]
    set_to_default: StrictBool = False


class GetMeasuresParams(BaseModel):
    measure_names: Optional[List[StrictStr]] = None
    return_id: Optional[StrictBool] = False


class CreateSphereParams(BaseModel):
    cube_name: StrictStr
    source_name: StrictStr
    file_type: StrictStr
    update_params: Optional[dict] = None
    sql_params: Optional[dict] = None
    user_interval: StrictStr = "с текущего дня"
    filepath: StrictStr = ""
    separator: StrictStr = ""
    increment_dim: StrictStr = ""
    interval_dim: StrictStr = ""
    interval_borders: Optional[list] = None
    encoding: StrictStr = ""
    delayed: StrictBool = False
    modified_records_params: Optional[dict] = None
    relevance_date: Optional[dict] = None
    indirect_cpu_load_parameter: Optional[dict] = None


class UpdateCubeParams(BaseModel):
    cube_name: StrictStr
    new_cube_name: Optional[StrictStr] = None
    update_params: Optional[dict] = None
    user_interval: StrictStr = "с текущего дня"
    filepath: StrictStr = ""
    separator: StrictStr = ""
    delayed: StrictBool = False
    increment_dim: StrictStr = ""
    interval_dim: StrictStr = ""
    interval_borders: Optional[list] = None
    encoding: StrictStr = ""
    modified_records_params: Optional[dict] = None
    relevance_date: Optional[dict] = None
    indirect_cpu_load_parameter: Optional[dict] = None


class CleanUpParams(BaseModel):
    cube_name: StrictStr
    dimension_name: StrictStr
    sql_params: dict
    is_update: StrictBool = True


class RenameDimsParams(BaseModel):
    dim_name: StrictStr
    new_name: StrictStr


class SetMeasureVisibilityParams(BaseModel):
    measure_names: Union[StrictStr, List[StrictStr]]
    is_visible: StrictBool = False


class DeleteDimFilterParams(BaseModel):
    dim_name: StrictStr
    filter_name: Union[StrictStr, list, set, tuple]
    num_row: StrictInt = 100


class CreateLayerParams(BaseModel):
    set_active: StrictBool = True


class CreateConsistentDimParams(BaseModel):
    formula: StrictStr
    separator: StrictStr
    dimension_list: List[StrictStr]
