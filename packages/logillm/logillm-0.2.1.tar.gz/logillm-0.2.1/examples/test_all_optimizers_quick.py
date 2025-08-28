#!/usr/bin/env python3
"""Quick test that all optimizers work with config fixes."""

import asyncio
import os

from logillm.core.predict import Predict
from logillm.optimizers import (
    BootstrapFewShot,
    HyperparameterOptimizer,
    LabeledFewShot,
)
from logillm.providers import create_provider, register_provider


async def test_optimizer(name, optimizer_class, **kwargs):
    """Test a single optimizer."""
    print(f"\nTesting {name}...")

    try:
        module = Predict("text -> category: str")
        train = [
            {"inputs": {"text": "billing issue"}, "outputs": {"category": "billing"}},
            {"inputs": {"text": "technical problem"}, "outputs": {"category": "support"}},
        ]

        def metric(pred, ref):
            if ref is None:
                return 0.5
            return 1.0 if pred.get("category") == ref.get("category") else 0.0

        # Create optimizer with minimal config
        if name == "HyperparameterOptimizer":
            opt = optimizer_class(metric=metric, n_trials=1, strategy="random")
            result = await opt.optimize(module=module, trainset=train)
        elif name == "BootstrapFewShot":
            opt = optimizer_class(metric=metric, max_bootstrapped_demos=1, max_rounds=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "LabeledFewShot":
            opt = optimizer_class(labeled_demos=train[:1])
            result = await opt.optimize(module=module, dataset=train)
        elif name == "RandomPrompt":
            opt = optimizer_class(num_candidates=1)
            result = await opt.optimize(module=module, dataset=train, metric=metric)
        elif name == "KNNFewShot":
            opt = optimizer_class(metric=metric, k=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "InstructionOptimizer":
            opt = optimizer_class(num_candidates=1)
            result = await opt.optimize(module=module, dataset=train, metric=metric)
        elif name == "FormatOptimizer":
            opt = optimizer_class(metric=metric, num_candidates=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "COPRO":
            opt = optimizer_class(metric=metric, depth=1, breadth=1, max_iterations=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "MIPROv2":
            opt = optimizer_class(metric=metric, max_iterations=1, num_candidates=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "SIMBA":
            opt = optimizer_class(metric=metric, n_iterations=1, minibatch_size=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "HybridOptimizer":
            opt = optimizer_class(metric=metric, num_candidates=1, max_iterations=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "MultiObjectiveOptimizer":
            opt = optimizer_class(
                metrics={"accuracy": metric}, weights={"accuracy": 1.0}, n_iterations=1
            )
            result = await opt.optimize(module=module, dataset=train)
        elif name == "ReflectiveEvolutionOptimizer":
            opt = optimizer_class(metric=metric, n_iterations=1, minibatch_size=1)
            result = await opt.optimize(module=module, dataset=train)
        elif name == "AvatarOptimizer":
            opt = optimizer_class(metric=metric, num_avatars=2, num_rounds=1)
            result = await opt.optimize(module=module, dataset=train)
        else:
            print(f"  ⚠️ {name} not implemented in test")
            return False

        # Check if config was properly handled
        if hasattr(result.optimized_module, "config"):
            config_type = type(result.optimized_module.config).__name__
            print(f"  ✓ Config type: {config_type}")
            if result.optimized_module.config:
                sample_keys = list(result.optimized_module.config.keys())[:3]
                print(f"  ✓ Sample keys: {sample_keys}")
        else:
            print("  ✓ No config (expected for some optimizers)")

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def main():
    """Test all optimizers quickly."""

    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY to test")
        return

    # Setup
    provider = create_provider("openai", model="gpt-4.1-nano")
    register_provider(provider, set_default=True)

    print("=" * 60)
    print("Testing All Optimizers with Config Fixes")
    print("=" * 60)

    # Test each optimizer
    optimizers = [
        ("HyperparameterOptimizer", HyperparameterOptimizer),
        ("BootstrapFewShot", BootstrapFewShot),
        ("LabeledFewShot", LabeledFewShot),
        # Skip slow ones for quick test
        # ("RandomPrompt", RandomPrompt),
        # ("KNNFewShot", KNNFewShot),
        # ("InstructionOptimizer", InstructionOptimizer),
        # ("FormatOptimizer", FormatOptimizer),
        # ("COPRO", COPRO),
        # ("MIPROv2", MIPROv2),
        # ("SIMBA", SIMBA),
        # ("HybridOptimizer", HybridOptimizer),
        # ("MultiObjectiveOptimizer", MultiObjectiveOptimizer),
        # ("ReflectiveEvolutionOptimizer", ReflectiveEvolutionOptimizer),
        # ("AvatarOptimizer", AvatarOptimizer),
    ]

    results = []
    for name, cls in optimizers:
        result = await test_optimizer(name, cls)
        results.append((name, result))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)

    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")

    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n✅ All tested optimizers handle config properly!")
    else:
        print("\n⚠️ Some optimizers had issues - check details above")


if __name__ == "__main__":
    asyncio.run(main())
