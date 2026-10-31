"""Read-only R3 full-policy record adapter; no solver, approval or replay.

Check saved identities, not scientific truth. In particular exchangeability is
not learned from the support table, and marginal support is not joint support.
"""
from copy import deepcopy
from . import network_observational_policy_dispatch as observational
from .business_dispatch import sha


def attempts(result, method_ids):
    recorded = result.get('attempts', [])
    if not recorded and result.get('backend_called') is not True:
        return {}
    if method_ids != {observational.METHOD}:
        raise ValueError('DIAGNOSTIC_EXACT_OBSERVATIONAL_METHOD_REQUIRED')
    if len(recorded) > 1 or any(r.get('method') != observational.METHOD for r in recorded):
        raise ValueError('DIAGNOSTIC_INVALID_OBSERVATIONAL_ATTEMPT')
    # The native attempt has no replay flag; only the completed answer has one.
    return {observational.METHOD: dict(
        state=(recorded[0]['state'] if recorded else 'NOT_ESTABLISHED'),
        reason_code=result.get('reason_code') or (recorded[0].get('reason_code') if recorded else None),
        raw_attempt=deepcopy(recorded[0]) if recorded else None,
        origin='EXISTING_OBSERVATIONAL_EXECUTOR_RECORD')}


def check_answer(plan, answer, attempt):
    """Match saved target, context, input and certificate; never re-prove R3."""
    try:
        target = plan['proposed_target']
        claim, certificate, native = (answer[k] for k in ('mathematical_claim','certificate','native_evidence'))
        study, nt, source = (native[k] for k in ('study','target','source'))
        if (not attempt or attempt['state'] != 'POINT' or claim['kind'] != 'POINT'
                or target['kind'] != 'FIXED_FULL_ASSIGNMENT_POLICY_MEAN'
                or native['route'] != observational.METHOD or certificate['route'] != observational.METHOD
                or native['status'] != 'POINT' or native['verification_status'] != 'VERIFIED'
                or native['signature'] is not None or native['sufficiency'] is not None
                or certificate['signature'] is not None
                or study['observation_regime'] != 'observational' or study['assignment_design_json'] is not None
                or nt['averaging_scope'] != 'population_conditional_mean_given_W'
                or study['treatment_variable'] != target['treatment']
                or study['node_order'] != target['node_order'] or source['node_order'] != target['node_order']
                or study['outcome_variable'] != target['outcome'] or source['outcome'] != target['outcome']
                or study['context_reference'] != target['context'] or source['context'] != target['context']):
            raise ValueError('target scope or native route')
        for public, internal in (('kind','kind'), ('node_order','node_order'), ('assignment','policy_assignment'),
                                 ('unit_weights','unit_weights'), ('outcome','outcome'), ('context','context')):
            if nt[internal] != target[public]:
                raise ValueError('native target coordinates')
        for key in ('status','verification_status','theorem_id','target_fingerprint','identified_functional',
                    'required_observables','target_observational_probability','certificate_sha256'):
            if certificate[key] != native[key]:
                raise ValueError('certificate summary')
        inquiry = {k:native[k] for k in ('study','target','source','assumptions','signature','sufficiency')}
        # The native study digest binds scope/protocol, not the entire dataclass.
        study_identity = sha(dict(scope=source['study_scope_digest'], protocol=source['protocol_digest']))
        if (sha(inquiry) != answer['reviewed_input_sha256'] or certificate['study_digest'] != study_identity
                or certificate['source_id'] != source['source_id'] or certificate['source_operator'] != source['operator']
                or claim['target_fingerprint'] != native['target_fingerprint']
                or claim['expression'] != native['identified_functional']
                or certificate['assumptions_used'] != [r['name'] for r in native['assumptions']]):
            raise ValueError('input or proof identity')
        classes = [dict(node=row[0], treatment=row[1], signature=row[2], support=support, weight=weight)
                   for row,support,weight in zip(native['weighted_node_classes'],native['node_support'],native['node_weights'])]
        if (not len(classes) == len(native['weighted_node_classes']) == len(native['node_support']) == len(native['node_weights'])
                or certificate['classes'] != classes):
            raise ValueError('summary evaluation scope')
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise ValueError('DIAGNOSTIC_INCOHERENT_OBSERVATIONAL_RECORD') from exc


def observational_view(plan):
    facts = plan.get('facts') or {}; study = facts.get('study') or {}
    return dict(origin='CURRENT_NATIVE_PLAN', checked_here=False,
        declared_target=deepcopy(facts.get('target')), prepared_target=deepcopy(plan.get('proposed_target')),
        regime=deepcopy(facts.get('regime')), business_context=study.get('context'),
        fixed_conditioning=deepcopy(facts.get('conditioning')),
        target_conditioning_review=deepcopy(plan.get('target_conditioning_review')),
        assumptions=deepcopy(facts.get('assumptions')), information=deepcopy(facts.get('information')),
        target_note='完整政策覆盖所有研究对象；评价名单及等权权重另行保留，固定W不改成跨背景平均。',
        exchangeability_note='条件交换性是须独立审核的科学假设，不由观察记录、总体概率或正支持自动证明。')


def decorate(item, plan, answer, result=None):
    item['calculation_contract'] = 'OBSERVATIONAL_FULL_POLICY_CONDITIONAL_MEAN_GIVEN_FIXED_W'
    support = dict(state='NOT_CHECKED', checked_here=False, probability=None,
        scope='COMPLETE_TARGET_ASSIGNMENT_GIVEN_FIXED_W',
        note='完整正概率安排表的声明不保证目标在表内；逐对象边际正支持不能替代完整政策联合正支持。')
    if answer:
        support.update(state='NATIVE_POSITIVE_SUPPORT_REPORTED', origin='EXISTING_EXECUTOR_RECORD',
                       probability=answer['certificate']['target_observational_probability'])
        item['certificate']['calculation_reported'] = 'NATIVE_R3_FULL_ASSIGNMENT_FIXED_W'
        item['certificate']['target_fingerprint'] = answer['mathematical_claim']['target_fingerprint']
    elif item.get('native_attempt'):
        code = item['native_attempt'].get('reason_code')
        support.update(state=('NATIVE_ZERO_SUPPORT_REPORTED' if code == 'ZERO_OBSERVATIONAL_FULL_ASSIGNMENT_SUPPORT'
                              else 'NOT_ESTABLISHED'), origin='EXISTING_EXECUTOR_RECORD', reason_code=code)
    item['joint_policy_support'] = support
