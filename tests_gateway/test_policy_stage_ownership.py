"""Exact compatibility is not semantic repair; audited intent has one owner."""
from copy import deepcopy
import json
import pytest
from cfm_id import business_intake as intake,business_dispatch as d,fact_reading_revision as revision
from cfm_id_llm import policy_action_compat as compat,policy_action_contract as strict
from cfm_id_llm.compact_wire_diagnostics import diagnose
from cfm_id_llm.compact_reference_contract import split_user
from jsonschema import Draft202012Validator
from tests_gateway.test_policy_interface_contracts import a0_case
from tests_gateway.test_inline_evidence_slots import receive
from tests_gateway.test_business_field_review import sheet,record,submit
from tests_gateway.test_reading_material_handoff import reviewed
from tests_gateway.test_fact_reading_revision import feedback,accept_changes
from examples.network_design_exposure_reference import material,fact_reference
from examples.network_dispatch_reference import approval_records


@pytest.mark.parametrize('family',['policy','contrast'])
def test_missing_direct_claim_is_located_without_repair_or_scientific_adoption(family):
    from cfm_id_llm.wire_type_diagnostics import diagnose as fact_diagnose
    from cfm_id_llm.fact_reading_contracts import contract_for_entry
    s,e,o=setup(family);raw=o['candidate']
    raw['mean_sufficiency'].update(status='NOT_STATED',source_ids=[],scope='UNKNOWN',covered_nodes=[],definition_refs=['study'])
    before=deepcopy(raw)
    rows=fact_diagnose(e,raw)
    assert rows[0]['field_path']=='/mean_sufficiency' and rows[0]['error_code']=='DIRECT_CLAIM_SOURCE_REQUIRED'
    with pytest.raises(ValueError,match='DIRECT_CLAIM_SOURCE_REQUIRED'):
        contract_for_entry(e).parse(e['bundle'],raw,binding=e['fact_binding_sha256'])
    w=revision.prepare_recheck(s,'q1',**o)['feedback_worksheet']
    r=revision.prepare_recheck(s,'q1',**o,feedback=feedback(w,path='/mean_sufficiency',kind='WIRE_FORMAT_ERROR',doc='study'))
    assert r['state']=='READY_TO_READ' and not r['backend_called']
    assert r['reading_revision']['steps'][0]['candidate']==before==raw
    assert not r['reading_revision_receipt']['scientific_approval']
    assert 'DIRECT_CLAIM_SOURCE_REQUIRED' in r['request']['user']


def test_diagnostic_accepts_absence_and_sourced_dependency_without_supplying_evidence():
    from cfm_id_llm.wire_type_diagnostics import diagnose as fact_diagnose
    s,e,o=setup();raw=o['candidate']
    assert fact_diagnose(e,raw)==[]
    raw['mean_sufficiency'].update(status='NOT_STATED',source_ids=[],scope='UNKNOWN',covered_nodes=[],definition_refs=[])
    assert fact_diagnose(e,raw)==[]


def setup(family='policy',*,alias=True,reverse=False):
    case,raw=a0_case(family)
    if alias:raw['queries'][0]['semantics']['policy_assignment']=deepcopy(raw['queries'][0]['semantics']['intervention'])
    if reverse:raw['queries'][0]['comparison_order']['operation']='COMPARATOR_MINUS_INTERVENTION'
    s=receive(case,raw,profile=compat.CONTRACT)
    s=intake.configure_network_fact_contract(s,'network-policy-scopes-1')
    s=intake.configure_material_handoff(s)
    q=submit(s,record(sheet(s)))['query_review'];e=d.prepare_reader(s,'q1',query_review=q)
    assert e['state']=='READY_TO_READ',e
    _,data=material('D1','E5',family)
    if reverse:data['first'],data['second']=data['second'],data['first']
    c=fact_reference(e,data);c['assignment']['definition_refs']=['study']
    c['mean_sufficiency']['definition_refs']=['study']
    for endpoint in ([c['target']] if family=='policy' else [c['target']['first'],c['target']['second']]):endpoint['definition_refs']=['study']
    for row in c['information']:row.update(definition_refs=['study'],scope_status='DECLARED',scope_source_ids=list(row['source_ids']))
    return s,e,dict(query_review=q,candidate=c,request_sha256=e['request_sha256'])


@pytest.mark.parametrize('alias',[False,True])
def test_only_exact_alias_is_compatible_without_modifying_raw_or_old_protocol(alias):
    case,raw=a0_case();sem=raw['queries'][0]['semantics']
    if alias:sem['policy_assignment']=deepcopy(sem['intervention'])
    s=receive(case,raw,profile=compat.CONTRACT);before=deepcopy(s.candidate);r=intake.inspect(s)
    assert 'report' in r and s.candidate==before
    receipt=r['wire_gate']['policy_action_projection']
    assert receipt['contract']==compat.CONTRACT and bool(receipt['compatible_aliases'])==alias
    assert not receipt['raw_candidate_modified']
    Draft202012Validator(split_user(intake.prepare_request(s)['user_prompt'])[2]).validate(s.candidate)
    assert 'queries.q1.semantics.policy_assignment' not in sheet(s)['fields']
    old=receive(case,raw,profile=strict.CONTRACT)
    assert ('report' in intake.inspect(old))== (not alias)
    assert intake.prepare_request(old)['system_prompt']==intake.prepare_request(s)['system_prompt']


@pytest.mark.parametrize('defect',['paraphrase','opposite','status','citations','duplicate_refs','missing_owner'])
def test_conflicts_and_unsupported_equivalence_do_not_gain_precedence(defect):
    case,raw=a0_case('contrast');sem=raw['queries'][0]['semantics'];sem['policy_assignment']=deepcopy(sem['intervention'])
    other=sem['policy_assignment']
    if defect=='paraphrase':other['value']+='。'
    elif defect=='opposite':sem['policy_assignment']=deepcopy(sem['comparator'])
    elif defect=='status':other['state']='INTERPRETED'
    elif defect=='citations':other['refs']=deepcopy(raw['common']['analysis_unit']['refs'])
    elif defect=='duplicate_refs':other['refs']*=2
    else:sem.pop('intervention')
    s=receive(case,raw,profile=compat.CONTRACT);before=deepcopy(s.candidate)
    assert 'report' not in intake.inspect(s) and d.prepare_reader(s,'q1')['request'] is None and s.candidate==before
    # Diagnostics use canonical refs here; neither source borrowing nor text repair.
    rows=diagnose(case,raw,response_contract=compat.CONTRACT)
    assert any(x['error_code']=='POLICY_ALIAS_CONFLICT' for x in rows),rows


@pytest.mark.parametrize('family,reverse',[('policy',False),('contrast',False),('contrast',True)])
def test_one_reviewed_intent_survives_fact_stage_and_native_replay(family,reverse):
    s,e,o=setup(family,reverse=reverse);raw=deepcopy(o['candidate'])
    text=e['request']['user'].split('本次只读取下面选定子问题。')[1]
    focus=json.JSONDecoder().raw_decode(text[text.index('{'):])[0]['focus']
    target=focus['reviewed_policy_target'];assert 'semantics' not in focus and 'requested_comparison_or_policy' not in focus
    assert 'policy_assignment' not in json.dumps(focus) and not target['is_citable_source'] and not target['scientific_approval']
    if family=='contrast':
        owner='comparator' if reverse else 'intervention'
        assert target['first']['value']==s.candidate['queries'][0]['semantics'][owner]['value']
        assert target['operation']=='FIRST_MINUS_SECOND'
    o['source_review']=reviewed(e,raw,omitted=False);p=d.inspect_methods(s,'q1',**o)
    assert not d.execute(s,'q1',**o,research_protocol_selected=True)['backend_called']
    r=d.execute(s,'q1',**o,**approval_records(p));assert r['state']=='POINT' and r['independent_replay'] and raw==o['candidate']


@pytest.mark.parametrize('defect',['pending_science','no_population','wrong_citation','alias_review_changed'])
def test_compatibility_and_intent_context_never_bypass_admission(defect):
    s,e,o=setup('contrast')
    if defect=='pending_science':o['candidate']['scientific_statements']['consistency']['status']='UNDECIDED'
    elif defect=='no_population':o['candidate']['information']=[]
    if defect=='alias_review_changed':
        value=s.model_dump(mode='json');value['candidate']['queries'][0]['semantics']['policy_assignment']['value']+='。'
        assert d.execute(value,'q1',**o)['backend_called'] is False;return
    review=reviewed(e,o['candidate'],omitted=False)
    if defect=='wrong_citation':review['decisions']['/target/first']['source_coverage']='REJECTED'
    r=d.execute(s,'q1',**o,source_review=review,research_protocol_selected=True)
    assert not r['backend_called'] and not r['independent_replay']


def test_recheck_rebuilds_same_intent_without_reusing_old_approvals(tmp_path):
    s,e,o=setup('contrast',reverse=True);o['source_review']=reviewed(e,o['candidate'],omitted=False)
    p=d.inspect_methods(s,'q1',**o);a=approval_records(p)
    args={k:v for k,v in o.items() if k!='source_review'}
    w=revision.prepare_recheck(s,'q1',**args)['feedback_worksheet']
    fresh=revision.prepare_recheck(s,'q1',**args,feedback=feedback(w,path='/target',doc='population'))
    assert fresh['reviewed_policy_request']==e['reviewed_policy_request']
    assert 'reviewed_policy_target' in fresh['request']['user']
    assert '原材料交接清单' in fresh['request']['user']
    assert not d.execute(s,'q1',**dict(o,request_sha256=fresh['request_sha256'],reading_revision=fresh['reading_revision']),**a)['backend_called']
    path=tmp_path/'intake.json';intake.save(s,path);assert intake.restore(path)==s
