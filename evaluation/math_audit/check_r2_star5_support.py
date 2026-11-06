"""Independently check R2 target-signature support in the Star-5 example."""

from fractions import Fraction

NODES = ("hub", "l1", "l2", "l3", "l4")
FULL_POLICY = (1, 1, 1, 1, 1)


def reference_support():
    """Count signature matches across the five equally likely trial lists."""
    leaves = set(NODES[1:])
    neighbors = {"hub": leaves}
    neighbors.update({leaf: {"hub"} for leaf in leaves})
    hits = dict.fromkeys(NODES, 0)

    # Each trial list omits exactly one node.
    for omitted in NODES:
        treated = set(NODES) - {omitted}
        for node, adjacent in neighbors.items():
            high_exposure = 2 * len(adjacent & treated) > len(adjacent)
            if node in treated and high_exposure:
                hits[node] += 1

    return sorted(
        ((node, 1, 1), Fraction(hits[node], len(NODES)))
        for node in NODES
    )


def main():
    from tests.test_verified_signature_policy_r2 import (
        get,
        replay_verified_signature_policy,
        study,
    )

    expected = reference_support()

    edges = tuple(("hub", leaf) for leaf in NODES[1:])
    context = study("D2", nodes=NODES, edges=edges)
    result = get(context, FULL_POLICY)

    actual = sorted(
        (tuple(cell), Fraction(support))
        for cell, support in zip(
            result.policy_node_classes, result.node_class_support, strict=True
        )
    )

    if Fraction(result.policy_assignment_probability) != 0:
        raise AssertionError("The full policy should have zero trial probability")
    if actual != expected:
        raise AssertionError(f"Expected signature supports {expected}, got {actual}")
    if not replay_verified_signature_policy(result):
        raise AssertionError("Original certificate failed replay")

    print("Full policy probability: 0")
    for (node, own, exposure), support in actual:
        print(f"{node} ({own}, {exposure}): {support} - match")
    print("Original replay: accepted")


if __name__ == "__main__":
    main()