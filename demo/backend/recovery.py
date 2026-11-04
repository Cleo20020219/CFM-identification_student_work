"""User-requested rereading of located notes; no candidate edits or approvals."""
from copy import deepcopy
from cfm_id import fact_reading_revision
from cfm_id_llm.fact_reading_contracts import contract_for_entry


def prepare(run, *, allow_busy=False):
    if (run.busy and not allow_busy) or run.review_kind not in ('source', 'notes', 'changes') or not run.submission:
        return {'available': False, 'items': []}
    args={k:run.submission[k] for k in ('query_review','candidate','request_sha256','reading_revision')
          if k in run.submission}
    candidate=args.get('candidate', {})
    located=[(f'/{name}/{i}',item) for name in ('additional_restrictions','unresolved')
             for i,item in enumerate(candidate.get(name,[])) if isinstance(item,dict)]
    if not located:return {'available': False, 'items': []}
    prepared=fact_reading_revision.prepare_recheck(run.intake,run.query_id,**args)
    sheet=prepared.get('feedback_worksheet')
    if not sheet:
        return {'available': False, 'items': [], 'reason': prepared.get('reason_code')}
    entry=run.entry
    contract=contract_for_entry(entry)
    refs=contract.reference_catalog(entry['bundle'],binding=entry['fact_binding_sha256'])
    aliases=refs['aliases'];items=[];issues=[]
    for path,item in located:
        source_ids=list(dict.fromkeys(aliases[ref]['source_id'] for ref in item.get('source_ids',[]) if ref in aliases))
        # Do not invent support for a note lacking locatable citations.
        if not source_ids:return {'available':False,'items':[], 'reason':'RECHECK_SOURCE_NOT_LOCATED'}
        quotes=[sheet['source_catalog'][sid].get('text','') for sid in source_ids]
        items.append(dict(path=path,text=item.get('text',''),quotes=quotes))
        issues.append(dict(field_path=path,kind='POSSIBLE_DUPLICATION',source_ids=source_ids,
                           reason='请求对照原材料核对该条说明的字段归属或遗漏；不指定替换值，不要求删除真实限制。'))
    if len(issues)>20:return {'available':False,'items':items,'reason':'TOO_MANY_RECHECK_ITEMS'}
    automatic=bool(run.automatic_review and allow_busy)
    feedback=dict(version=sheet['version'],binding_sha256=sheet['binding_sha256'],authority=run.authority,
        reviewer='Background reading recovery' if automatic else 'Local browser user',
        evidence=('后台按已启用的读取流程请求模型核对说明归属，并非用户逐条审核；不接受候选、不批准科学条件。'
                  if automatic else '用户明确请求模型核对列出的说明与原文；此次操作不接受候选、不批准任何科学条件。'),issues=issues)
    return dict(available=True,items=items,binding_sha256=sheet['binding_sha256'],
                feedback=feedback,args=deepcopy(args),is_approval=False)


def public(plan):
    return {k:v for k,v in plan.items() if k not in ('args','feedback')}


def request(run,binding, *, allow_busy=False):
    plan=prepare(run,allow_busy=allow_busy)
    if not plan['available']:raise ValueError('NO_LOCATED_RECHECK_AVAILABLE')
    if binding!=plan['binding_sha256']:raise ValueError('STALE_RECHECK_PREVIEW')
    entry=fact_reading_revision.prepare_recheck(run.intake,run.query_id,**plan['args'],feedback=plan['feedback'])
    if entry['state']!='READY_TO_READ':raise ValueError('RECHECK_PREPARATION_BLOCKED')
    return entry,plan['feedback']
