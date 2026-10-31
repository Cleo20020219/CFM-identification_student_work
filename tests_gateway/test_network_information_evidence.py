"""Supporting citations need explicit provenance review, never source deletion."""
from copy import deepcopy
import pytest
from cfm_id import business_dispatch as dispatch, network_information_evidence as evidence
from tests_gateway.test_network_bounded_dispatch import setup, execute, partition_table, forbidden
from examples.network_dispatch_reference import approval_records

def fixture(**kw):
    s,e,o,p=setup(**kw)
    o['candidate']['information'][0]['source_ids']+=o['candidate']['exposure']['source_ids']
    w=evidence.prepare(e,o['candidate'])
    table=[sid for sid,v in w['source_catalog'].items() if v['doc_id']=='information']
    rec=dict(version=w['version'],binding_sha256=w['binding_sha256'],authority='SYNTHETIC_TEST',reviewer='independent_fixture_audit',
        evidence='Exact numerical cells occur in one original table; the other document only defines the signature. All original references retained. Science reviewed separately.',
        disposition='ACCEPTED',table_source_ids=table,supporting_source_ids=[sid for sid in w['source_catalog'] if sid not in table])
    assert table and rec['supporting_source_ids']
    return s,e,o,rec

@pytest.mark.parametrize('bounds,expected',[(('1/2','1/2'),'POINT'),(('1/4','3/4'),'PARTIAL')])
def test_one_table_with_supporting_evidence_replays_identical_mathematics(bounds,expected):
    original_s,_,original_o,_=setup(center_bounds=bounds);baseline=execute(original_s,original_o)
    s,e,o,rec=fixture(center_bounds=bounds);raw=deepcopy(o['candidate'])
    assert dispatch.inspect_methods(s,'q1',**o)['reason_code']=='EXACT_SINGLE_SOURCE_TABLE_REQUIRED'
    p=dispatch.inspect_methods(s,'q1',**o,information_evidence_review=rec)
    assert p['state']=='REVIEW_REQUIRED' and p['a4_projection']['table_documents']==['information']
    assert not dispatch.execute(s,'q1',**o,information_evidence_review=rec,research_protocol_selected=True)['backend_called']
    r=dispatch.execute(s,'q1',**o,information_evidence_review=rec,**approval_records(p))
    assert r['state']==expected and r['independent_replay'] and r['mathematical_claim']['sharp']
    assert r['mathematical_claim']==baseline['mathematical_claim'] and o['candidate']==raw
    receipt=r['information_evidence_receipt'];assert not receipt['scientific_approval'] and not receipt['information_entries_merged']
    native=r['answers'][0]['native_evidence']
    assert native['information']['values']==baseline['answers'][0]['native_evidence']['information']['values']
    assert native['information']['bounds']==baseline['answers'][0]['native_evidence']['information']['bounds']
    assert not r['production_admission'] and not r['estimation_handoff_allowed']

@pytest.mark.parametrize('bad',['pending','rejected','overlap','omitted','two_table_docs','foreign','authority','stale_candidate','stale_request'])
def test_invalid_unapproved_or_stale_source_roles_never_call_math(bad,monkeypatch):
    from cfm_id import bounded_policy_solver
    monkeypatch.setattr(bounded_policy_solver,'solve',forbidden)
    s,e,o,rec=fixture()
    if bad=='pending':rec['disposition']='PENDING'
    elif bad=='rejected':rec['disposition']='REJECTED'
    elif bad=='overlap':rec['supporting_source_ids']+=rec['table_source_ids']
    elif bad=='omitted':rec['supporting_source_ids']=[]
    elif bad=='two_table_docs':rec['table_source_ids']+=rec['supporting_source_ids'];rec['supporting_source_ids']=[]
    elif bad=='foreign':rec['supporting_source_ids']=['not-a-current-source']
    elif bad=='authority':rec['authority']='EXTERNAL_RESEARCH_REVIEW'
    elif bad=='stale_candidate':o['candidate']['target']['population']=['中心']
    else:rec['binding_sha256']='0'*64
    r=dispatch.execute(s,'q1',**o,information_evidence_review=rec,research_protocol_selected=True)
    assert not r['backend_called'] and r['mathematical_claim'] is None and not r['answers']

def test_multiple_information_entries_are_not_merged_by_evidence_review():
    s,e,o,rec=fixture();partition_table(o['candidate'])
    with pytest.raises(ValueError,match='SINGLE_NETWORK_INFORMATION'):evidence.prepare(e,o['candidate'])
    r=dispatch.execute(s,'q1',**o,information_evidence_review=rec,research_protocol_selected=True)
    assert not r['backend_called'] and r['mathematical_claim'] is None

@pytest.mark.parametrize('block',['sufficiency','bounds','additional','coupling','duplicate'])
def test_valid_source_role_review_does_not_release_independent_blockers(block,monkeypatch):
    from cfm_id import bounded_policy_solver
    monkeypatch.setattr(bounded_policy_solver,'solve',forbidden)
    s,e,o,rec=fixture();c=o['candidate']
    if block=='sufficiency':c['mean_sufficiency']['value']=False
    elif block=='bounds':c['bounded_model']['bounds_scope']='UNKNOWN'
    elif block=='additional':c['additional_restrictions']=[dict(text='还另行采用跨对象均值相等限制，尚未接入该模型。',source_ids=c['study']['source_ids'])]
    elif block=='coupling':c['bounded_model']['no_additional_coupling_constraints']['value']=False
    else:c['information'][0]['signature_cells'].append(deepcopy(c['information'][0]['signature_cells'][0]))
    # Re-review source roles against the actual new candidate, without science approval.
    try:rec['binding_sha256']=evidence.prepare(e,c)['binding_sha256']
    except ValueError:pass
    r=dispatch.execute(s,'q1',**o,information_evidence_review=rec,research_protocol_selected=True)
    assert not r['backend_called'] and r['mathematical_claim'] is None

def test_plain_single_document_path_and_default_remain_unchanged():
    s,e,o,p=setup()
    assert dispatch.inspect_methods(s,'q1',**o)==p
    with pytest.raises(ValueError,match='MULTIDOCUMENT_EVIDENCE'):evidence.prepare(e,o['candidate'])

def test_offline_cli_exposes_separate_evidence_worksheet_and_review(tmp_path):
    from cfm_id import business_intake as intake
    from cfm_id.business_dispatch_cli import main
    s,e,o,rec=fixture()
    intake.save(s,tmp_path/'intake.json')
    for name,value in [('entry',e),('query',e['query_review']),('candidate',o['candidate']),('evidence',rec)]:intake.write_json(tmp_path/(name+'.json'),value)
    args=['--intake',str(tmp_path/'intake.json'),'--query','q1','--query-review',str(tmp_path/'query.json'),
          '--reader-plan',str(tmp_path/'entry.json'),'--candidate',str(tmp_path/'candidate.json')]
    assert main(['information-evidence-plan',*args,'--output',str(tmp_path/'worksheet.json')])==0
    w=intake.read_json(tmp_path/'worksheet.json');assert not w['backend_called'] and not w['scientific_approval']
    assert main(['method-plan',*args,'--information-evidence-review',str(tmp_path/'evidence.json'),'--output',str(tmp_path/'methods.json')])==0
    p=intake.read_json(tmp_path/'methods.json');assert p['state']=='REVIEW_REQUIRED' and not p['backend_called'] and p['plan_worksheet']
