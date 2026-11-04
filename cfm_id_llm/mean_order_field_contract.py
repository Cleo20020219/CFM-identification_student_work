"""Public wire rules for the existing ordered-mean projection, not mathematics.

Descriptions, JSON Schema, parsing and recheck diagnostics share this owner.
Unknown adoption and extra constraints remain valid readings, never approvals.
The old standalone reader and its mathematical backend are not modified.
"""
from copy import deepcopy
import json
from pydantic import ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError
from cfm_id.mean_order_reading import OrderClaim as NativeClaim, OrderReading as NativeReading


NULL_RULE = dict(code='NOT_ASSUMED_HAS_NO_LICENSED_LEVEL_OR_SCOPE',
    trigger_field='relation', trigger='NOT_ASSUMED', required_null_fields=('level','scope'),
    description='明确不采用该顺序时，没有获准的层级和范围，level与scope都为null。尚未决定采用应保留UNKNOWN，不能为了通过格式改为不采用或已采用。')


def combination_schema():
    return {'if': {'properties': {NULL_RULE['trigger_field']: {'const': NULL_RULE['trigger']}},
                   'required': [NULL_RULE['trigger_field']]},
            'then': {'properties': {k: {'type': 'null'} for k in NULL_RULE['required_null_fields']}}}


class OrderClaim(NativeClaim):
    model_config = ConfigDict(json_schema_extra={'allOf': [combination_schema()],
        'x-cfm-field-contract': [dict(error_code=NULL_RULE['code'], description=NULL_RULE['description'],
                                    combination=combination_schema())]})
    nodes: list[str] | None = Field(description='该顺序条件适用的对象，不是本题评价子集。展开名单须引用名单定义；范围不明用null。')
    axis: NativeClaim.model_fields['axis'].annotation = Field(description='OWN：只改变本人，其他安排固定；PEERS：本人及其他安排固定，只增加一个合作邻居使用；轴不明为UNKNOWN。')
    relation: NativeClaim.model_fields['relation'].annotation = Field(description='NONDECREASING：明确提出拟采用数值均值非减；这是所提条件的关系，不是批准状态。NOT_ASSUMED：明确不采用该条件；UNKNOWN：是否提出采用尚未决定或含义未清。明确提出拟采用与尚未决定采用不同。未提及不能补为不采用。NO_EFFECT是无影响，NONINCREASING是非增，均不得改写成不采用或非减。任何关系仍须独立科学审核才可用于求解。')
    level: NativeClaim.model_fields['level'].annotation = Field(description='约束均值为CONDITIONAL_MEAN，约束每次结果为EACH_OUTCOME，不自动弱化；未说清为UNKNOWN/null。relation为NOT_ASSUMED时必须null。')
    scope: NativeClaim.model_fields['scope'].annotation = Field(description='覆盖所有完整二元安排（含试点外）为ALL_BINARY_ASSIGNMENTS，仅试点为HISTORICAL_SUPPORT；未说清为UNKNOWN/null。relation为NOT_ASSUMED时必须null。')
    basis: NativeClaim.model_fields['basis'].annotation = Field(description='ASSUMPTION_STATEMENT包括提出、拒绝或尚未决定采用的科学声明；OBSERVED_PATTERN只是观察到的现象，不能转成科学许可；依据未明为UNKNOWN。')

    @model_validator(mode='after')
    def check_combination(self):
        if (getattr(self, NULL_RULE['trigger_field']) == NULL_RULE['trigger']
                and any(getattr(self, k) is not None for k in NULL_RULE['required_null_fields'])):
            raise PydanticCustomError(NULL_RULE['code'], NULL_RULE['description'])
        return self


class OrderReading(NativeReading):
    claims: list[OrderClaim] = Field(max_length=48,
        description='每个模型对象的OWN、PEERS分别读取；同一条件可列多个对象。缺失的轴不默认不采用，每个对象每轴至多一条。')
    reported_conflict: bool | None = Field(description='只记录原材料是否有相互矛盾的科学声明：发现冲突为true，未发现为false；仅材料明确留有无法判断的冲突时为null。未决定采用、缺项、等待审核都不等于冲突。false不授予科学许可。')
    other_restriction_source_ids: list[str] = Field(description='只引用顺序模型之外尚未适配的真实限制，如跨对象等式、额外平滑性；没有则[]。基础科学条件、均值充分性、界限、精确总体均值及已表达的顺序不是此栏额外限制。“除此之外无约束”的声明不是额外约束来源；真实额外限制不能删除。')


COMPLETE_MODEL = ('只读取是否明确声明“除基础条件、均值充分性、界限和已列顺序外没有其他约束”：'
    '明确如此为true；明确还采用其他约束为false；此完整性声明未提供或未定为null。'
    '某条顺序尚未决定不自动改变这项独立声明，已有顺序也不等于另有未列约束。')


def validation_diagnostic(error):
    if error['type'] != NULL_RULE['code']:
        return {}
    return dict(error_code=NULL_RULE['code'], description=NULL_RULE['description'],
                combination=combination_schema())


def field_constraints(paths, *, request):
    """Derive recheck context from the same first-request schema, never gold."""
    schema=json.JSONDecoder().raw_decode(request['user'])[0]['output_schema']
    node=schema.get('properties',{}).get('mean_order_model')
    if node is None:return []
    rows=[];defs=schema.get('$defs',{})
    def walk(value,path):
        if '$ref' in value:return walk(defs[value['$ref'].split('/')[-1]],path)
        if value.get('description'):rows.append(dict(field_path=path,description=value['description']))
        rows.extend(dict(field_path=path,**deepcopy(rule)) for rule in value.get('x-cfm-field-contract',[]))
        for key,child in value.get('properties',{}).items():walk(child,path+'/'+key)
        if 'items' in value:walk(value['items'],path+'/*')
        for child in value.get('anyOf',[]):walk(child,path)
    walk(node,'/mean_order_model')
    def normalized(path):return '/'.join('*' if part.isdigit() else part for part in path.split('/'))
    return [row for row in rows if any(not p or normalized(p)==row['field_path']
        or normalized(p).startswith(row['field_path']+'/') or row['field_path'].startswith(normalized(p)+'/') for p in paths)]
