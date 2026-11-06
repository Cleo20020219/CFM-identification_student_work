"""Independently check R1a arm support and reject a wrong probability."""

from fractions import Fraction
from itertools import combinations
from unittest.mock import patch


def reference_support():
    """Count the D2/E1 arm (1, 0) for node 0 across legal assignments."""
    allocations = list(combinations(("0", "1", "2", "3"), 2))
    hits = 0
    for allocation in allocations:
        treated = set(allocation)
        high_exposure = 2 * len(treated & {"1", "2"}) > 2
        if "0" in treated and not high_exposure:
            hits += 1
    return Fraction(hits, len(allocations)), hits, len(allocations)


def main():
    from tests.test_randomized_arm_abstraction import (
        ArmSupportEvidence,
        AssignmentSpec,
        CompleteRandomizationDesignV1,
        ExposureSpec,
        IdentificationVerifier,
        NetworkExposureSpec,
        RandomizedNetworkArmBackend,
        SupportEngine,
        make_complete_randomization_arm_spec,
    )

    expected, hits, total = reference_support()
    network = NetworkExposureSpec(
        network_id="proof-gate",
        node_ids=["0", "1", "2", "3"],
        undirected_edges=[("0", "1"), ("0", "2")],
    )
    evidence = SupportEngine.evaluate(
        network=network,
        assignment=AssignmentSpec(CompleteRandomizationDesignV1(m=2)),
        exposure=ExposureSpec("strict_majority_ties_low"),
        node_id="0",
        own_treatment_value=1,
        exposure_value=0,
    )
    if evidence.joint_probability != expected:
        raise AssertionError(f"Expected {expected}, got {evidence.joint_probability}")

    spec = make_complete_randomization_arm_spec(
        network, m=2, node_id="0", own_treatment_value=1, exposure_value=0,
        source="synthetic protocol", evidence="known complete randomization",
        admitted=True, synthetic=True, query_authority="TRUSTED_FIXTURE",
    )
    backend = RandomizedNetworkArmBackend()
    verifier = IdentificationVerifier()
    original = backend.solve(spec)

    # These probabilities multiply correctly but disagree with the design.
    wrong_support = ArmSupportEvidence(
        Fraction(1, 2), Fraction(1, 2), Fraction(1, 4)
    )
    with patch.object(SupportEngine, "evaluate", return_value=wrong_support):
        changed = backend.solve(spec)
        original_status = verifier.verify(spec, original).verification_status
        changed_status = verifier.verify(spec, changed).verification_status

    if original_status != "VERIFIED" or changed_status != "REJECTED":
        raise AssertionError(f"Unexpected replay results: {original_status}, {changed_status}")

    print(f"Arm support: {hits}/{total} = {expected} - match")
    print("Original result during patch: VERIFIED")
    print("Internally consistent but wrong probability: REJECTED")


if __name__ == "__main__":
    main()