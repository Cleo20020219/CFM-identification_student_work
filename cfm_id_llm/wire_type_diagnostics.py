"""Advisory type errors from fixed reader models; never repair a candidate.

This is not complete request JSON Schema validation, source entailment, scientific
review or mathematical verification. No provider, solver or dynamic model import.
"""
from pydantic import ValidationError


def _model(entry):
    # Preserve this import surface; selection has one runtime owner shared with
    # source review. A missing/unknown contract remains advisory, not approval.
    from .fact_wire_models import model_for
    try:
        return model_for(entry)
    except (ValueError, TypeError):
        return None


def diagnose(entry, candidate):
    """Return bounded diagnostics, without raw values or free-text validator errors."""
    model = _model(entry)
    if model is None:
        return []
    try:
        parsed = model.model_validate(candidate)
    except ValidationError as exc:
        rows = []
        for error in exc.errors(include_input=False, include_url=False)[:50]:
            # Custom value_error messages can contain arbitrary candidate data;
            # only type codes and model-owned Literal alternatives are public.
            row = dict(field_path=''.join('/'+str(p).replace('~','~0').replace('/','~1')
                                          for p in error['loc']), error_code=error['type'])
            if error['type'] == 'literal_error':
                expected = error.get('ctx', {}).get('expected')
                if type(expected) is str and len(expected) <= 4000:
                    row['allowed_literals'] = expected
            rows.append(row)
        return rows
    except (ValueError, TypeError, ArithmeticError):
        # Advisory diagnostics must not disable the pre-existing source recheck
        # when an old custom validator raises an unwrapped arithmetic error.
        return []
    if entry.get('reader_id') == 'NETWORK_RANDOMIZED_EFFECT_FACTS':
        from .effect_information_rules import diagnose as effect_diagnostics
        return effect_diagnostics(parsed.information)
    if entry.get('network_fact_contract') in ('network-source-selections-information-1', 'network-source-selections-information-2') and entry.get('reader_id') in ('NETWORK_FIXED_POLICY_FACTS', 'NETWORK_POLICY_CONTRAST_FACTS'):
        from .information_field_rules import diagnose as information_diagnostics
        return information_diagnostics(parsed.information)
    return []
