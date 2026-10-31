"""Independent provenance review for one exact table with supporting documents.

This classifies evidence roles, not A4 truth or scientific assumptions. It never
edits the candidate, combines information entries, or invokes mathematics.
"""
from typing import Literal
from pydantic import Field
from .fact_reading_revision import StrictRecord
from .business_dispatch import sha, DispatchError
from .source_locations import build_catalog
from cfm_id_llm.network_policy_reading import documents, NetworkPolicyReading
from cfm_id_llm.network_fact_protocols import network_fact_protocol

VERSION='network-information-evidence-review-1'

class InformationEvidenceReview(StrictRecord):
    version: Literal['network-information-evidence-review-1']=VERSION
    binding_sha256: str=Field(pattern=r'^[0-9a-f]{64}$')
    authority: Literal['SYNTHETIC_TEST','EXTERNAL_RESEARCH_REVIEW']
    reviewer: str=Field(min_length=3,max_length=200)
    evidence: str=Field(min_length=12,max_length=3000)
    disposition: Literal['ACCEPTED','REJECTED','PENDING']
    table_source_ids: list[str]=Field(min_length=1,max_length=64)
    supporting_source_ids: list[str]=Field(max_length=64)

def _worksheet(entry,raw,c):
    if entry.get('reader_id')!='NETWORK_FIXED_POLICY_FACTS' or len(c.information)!=1:
        raise ValueError('SINGLE_NETWORK_INFORMATION_ENTRY_REQUIRED')
    info=c.information[0]
    if info.operator!='NODE_SIGNATURE_MEANS' or info.availability!='EXACT_POPULATION_VALUE':
        raise ValueError('EXACT_SIGNATURE_TABLE_REQUIRED')
    catalog=build_catalog(documents(entry['bundle']))
    ids=list(dict.fromkeys(info.source_ids))
    if len({catalog[s]['doc_id'] for s in ids})<2:
        raise ValueError('MULTIDOCUMENT_EVIDENCE_REQUIRED')
    binding=sha(dict(version=VERSION,request_sha256=entry['request_sha256'],
        fact_binding_sha256=entry['fact_binding_sha256'],bundle=entry['bundle'],
        query_review=entry['query_review'],candidate=raw))
    return dict(version=VERSION,binding_sha256=binding,expected_authority=entry['query_review']['authority'],
        source_catalog={s:catalog[s] for s in ids},information=info.model_dump(mode='json'),
        instruction='独立确认全部精确格子来自同一个原始信息表；其他引用仅用于解释对象、编码、暴露或期间，不包含另一份总体信息、额外方程或约束。无法确认就保持PENDING或拒绝，不能删除引用来通过。此审核不批准科学条件。',
        scientific_approval=False,is_approval=False)

def prepare(entry,raw):
    decoded=network_fact_protocol(entry.get('network_fact_contract')).parse(entry['bundle'],raw,binding=entry['fact_binding_sha256'])
    c=NetworkPolicyReading.model_validate(decoded['facts'])
    return _worksheet(entry,raw,c)

def check(entry,raw,c,record):
    w=_worksheet(entry,raw,c)
    r=InformationEvidenceReview.model_validate(record)
    if r.binding_sha256!=w['binding_sha256'] or r.authority!=w['expected_authority'] or not r.reviewer.strip() or not r.evidence.strip():
        raise ValueError('STALE_OR_WRONG_AUTHORITY_INFORMATION_EVIDENCE_REVIEW')
    ids=r.table_source_ids+r.supporting_source_ids
    if len(ids)!=len(set(ids)) or set(ids)!=set(w['source_catalog']):
        raise ValueError('EXACT_DISJOINT_SOURCE_ROLE_COVERAGE_REQUIRED')
    table_docs={w['source_catalog'][s]['doc_id'] for s in r.table_source_ids}
    if len(table_docs)!=1:
        raise ValueError('ONE_ORIGINAL_TABLE_DOCUMENT_REQUIRED')
    if r.disposition=='REJECTED':raise DispatchError('CHECK_BLOCKED','INFORMATION_EVIDENCE_REVIEW_REJECTED')
    if r.disposition!='ACCEPTED':raise DispatchError('REVIEW_REQUIRED','INFORMATION_EVIDENCE_REVIEW_PENDING')
    return dict(version=VERSION,review=r.model_dump(mode='json'),review_sha256=sha(r.model_dump(mode='json')),
        table_documents=sorted(table_docs),supporting_documents=sorted({w['source_catalog'][s]['doc_id'] for s in r.supporting_source_ids}),
        candidate_modified=False,information_entries_merged=False,scientific_approval=False)
