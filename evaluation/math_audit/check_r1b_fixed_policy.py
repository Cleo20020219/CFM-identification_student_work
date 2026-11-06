"""Check R1b assignment probability, formula, and certificate replay."""

from dataclasses import replace
from fractions import Fraction
from itertools import product

NODES = ("a", "b", "c", "d")
ASSIGNMENT = (1, 0, 1, 0)
WEIGHTS = ("2/3", "0", "1/3", "0")
CONTEXT = "W:business"


def reference_probability():
    """Count equally likely draws for propensities 1/3, 1/2, 2/3, 1/4."""
    hits = total = 0
    for a, b, c, d in product(range(3), range(2), range(3), range(4)):
        assignment = (int(a < 1), int(b < 1), int(c < 2), int(d < 1))
        total += 1
        if assignment == ASSIGNMENT:
            hits += 1
    return Fraction(hits, total), hits, total


def main():
    from pfn_pipeline.identification_a4_shadow import _sha
    from pfn_pipeline.identification_policy_r1b import (
        R1bPolicyUnavailable,
        _result_payload,
        identify_verified_fixed_policy,
        replay_verified_fixed_policy,
    )
    from tests.test_verified_fixed_policy_r1b import a4, assumptions, make_study, target

    expected_probability, hits, total = reference_probability()
    expected_observables = (
        "E[Y_{a}^obs | W=W:business, T_vector=(1,0,1,0)]",
        "E[Y_{c}^obs | W=W:business, T_vector=(1,0,1,0)]",
    )
    a_mean, c_mean = expected_observables
    expected_formula = f"2/3 * {a_mean} + 1/3 * {c_mean}"

    study = make_study("D1")
    policy = target(study, weights=WEIGHTS)
    if (tuple(study.node_order), tuple(policy.policy_assignment), policy.context) != (
        NODES, ASSIGNMENT, CONTEXT
    ):
        raise AssertionError("The fixture no longer matches the reference case")

    source = a4(study, nodes=("a", "c"))
    result = identify_verified_fixed_policy(
        study, policy, (source,), assumptions=assumptions()
    )

    actual_probability = Fraction(result.assignment_probability)
    if actual_probability != expected_probability:
        raise AssertionError(f"Unexpected assignment probability: {actual_probability}")
    if tuple(result.required_observables) != expected_observables:
        raise AssertionError(f"Unexpected observables: {result.required_observables}")
    if result.identified_functional != expected_formula:
        raise AssertionError(f"Unexpected formula: {result.identified_functional}")
    if not replay_verified_fixed_policy(result):
        raise AssertionError("Original certificate failed replay")

    changed = replace(
        result, identified_functional=f"1/3 * {a_mean} + 2/3 * {c_mean}"
    )
    changed = replace(changed, certificate_sha256=_sha(_result_payload(changed)))

    try:
        replay_verified_fixed_policy(changed)
    except R1bPolicyUnavailable as exc:
        if exc.reason_code != "POLICY_CERTIFICATE_REPLAY_MISMATCH":
            raise
    else:
        raise AssertionError("Replay accepted swapped node coefficients")

    print(f"Assignment probability: {hits}/{total} = {actual_probability} - match")
    print("Formula and required observables: match")
    print("Original replay: accepted")
    print("Swapped coefficients after rehash: rejected")


if __name__ == "__main__":
    main()