"""Check the R3-Full formula and rejection of a wrong assignment."""

from dataclasses import asdict, replace
from fractions import Fraction

NODES = ("n0", "n1", "n2")
TARGET = (1, 0, 1)
OTHER_ASSIGNMENT = (0, 0, 0)
CONTEXT = "W=w0"


def reference_formula(assignment):
    """Write the three expected terms for the fixed equal-weight example."""
    return " + ".join(
        f"1/3 * E[Y_{{{node}}}^obs | T={assignment}, W={CONTEXT}]"
        for node in NODES
    )


def main():
    from pfn_pipeline.identification_a4_shadow import _sha
    from pfn_pipeline.identification_observational_r3 import (
        R3Unavailable,
        identify_observational_policy_v23,
        replay_observational_policy_v23,
    )
    from tests.test_observational_r3_and_signature_diagnostics import (
        a5,
        population,
        study,
        target,
    )

    context = study()
    source = population(
        context, [(OTHER_ASSIGNMENT, Fraction(1, 3)), (TARGET, Fraction(2, 3))]
    )
    policy = target(context, TARGET)
    result = identify_observational_policy_v23(
        context, policy, source, assumptions=a5()
    )

    if result.route != "R3_FULL_ASSIGNMENT":
        raise AssertionError(f"Unexpected route: {result.route}")
    if Fraction(result.target_observational_probability) != Fraction(2, 3):
        raise AssertionError("Unexpected observational probability")
    if result.identified_functional != reference_formula(TARGET):
        raise AssertionError(f"Unexpected formula: {result.identified_functional}")
    if not replay_observational_policy_v23(result):
        raise AssertionError("Original certificate failed replay")

    changed = replace(
        result, identified_functional=reference_formula(OTHER_ASSIGNMENT)
    )
    payload = asdict(changed)
    payload.pop("certificate_sha256")
    changed = replace(changed, certificate_sha256=_sha(payload))

    try:
        replay_observational_policy_v23(changed)
    except R3Unavailable as exc:
        if str(exc) != "R3_CERTIFICATE_REPLAY_MISMATCH":
            raise
    else:
        raise AssertionError("Replay accepted a formula for the wrong assignment")

    print("Target observational probability: 2/3 - match")
    print("Three formula terms: match")
    print("Original replay: accepted")
    print("Wrong supported assignment after rehash: rejected")


if __name__ == "__main__":
    main()