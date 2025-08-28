#!/usr/bin/env python3
"""Simple proof that hyperparameters and prompts are actually updated during optimization."""

import asyncio
import os

from logillm.core.predict import Predict
from logillm.optimizers import BootstrapFewShot, HyperparameterOptimizer
from logillm.providers import create_provider, register_provider


def inspect_config(module, label="Module"):
    """Print module configuration."""
    print(f"\n{label} Configuration:")
    print("-" * 40)
    if hasattr(module, "config") and module.config:
        for key, value in module.config.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    else:
        print("  No config (using defaults)")

    if hasattr(module, "demo_manager") and module.demo_manager and module.demo_manager.demos:
        print(f"  Demos: {len(module.demo_manager.demos)} examples")
    else:
        print("  Demos: 0 examples")


async def main():
    """Prove that optimization actually changes configurations."""

    if not os.getenv("OPENAI_API_KEY"):
        print("Please set: export OPENAI_API_KEY=your_key")
        return

    print("=" * 60)
    print("PROOF: Hyperparameters and Prompts DO Change")
    print("=" * 60)

    # Setup
    provider = create_provider("openai", model="gpt-4.1-nano")
    register_provider(provider, set_default=True)

    # Create module
    classifier = Predict("text -> category: str")

    # Training data (small for speed)
    train_data = [
        {"inputs": {"text": "I need help with my bill"}, "outputs": {"category": "billing"}},
        {"inputs": {"text": "The product is broken"}, "outputs": {"category": "support"}},
        {"inputs": {"text": "Do you have this in blue?"}, "outputs": {"category": "sales"}},
    ]

    # 1. INITIAL STATE
    print("\n1️⃣ BEFORE ANY OPTIMIZATION")
    inspect_config(classifier, "INITIAL")
    test1 = await classifier(text="My payment failed")
    print(f"  Test output: {test1.outputs}")

    # 2. HYPERPARAMETER OPTIMIZATION
    print("\n2️⃣ AFTER HYPERPARAMETER OPTIMIZATION")
    print("Running hyperparameter optimization...")

    def simple_metric(pred, ref):
        if ref is None:
            return 0.5
        return 1.0 if pred.get("category") == ref.get("category") else 0.0

    # Optimize hyperparameters
    hyper_opt = HyperparameterOptimizer(
        metric=simple_metric,
        n_trials=3,  # Just a few trials for demo
        strategy="random",  # Fixed: use 'strategy' not 'search_strategy'
        verbose=False,
    )

    param_space = {"temperature": (0.1, 0.9), "top_p": (0.5, 1.0), "max_tokens": [50, 100, 150]}

    result1 = await hyper_opt.optimize(
        module=classifier,
        trainset=train_data,  # Fixed: use 'trainset' not 'dataset'
        param_space=param_space,
    )

    classifier_with_hyperparams = result1.optimized_module
    inspect_config(classifier_with_hyperparams, "AFTER HYPERPARAMETER OPT")
    test2 = await classifier_with_hyperparams(text="My payment failed")
    print(f"  Test output: {test2.outputs}")

    # 3. PROMPT OPTIMIZATION (adds demonstrations)
    print("\n3️⃣ AFTER PROMPT OPTIMIZATION")
    print("Running prompt optimization (adds few-shot examples)...")

    prompt_opt = BootstrapFewShot(
        metric=simple_metric, max_bootstrapped_demos=2, max_labeled_demos=2
    )

    result2 = await prompt_opt.optimize(module=classifier_with_hyperparams, dataset=train_data)

    fully_optimized = result2.optimized_module
    inspect_config(fully_optimized, "AFTER PROMPT OPT")
    test3 = await fully_optimized(text="My payment failed")
    print(f"  Test output: {test3.outputs}")

    # 4. PROOF SUMMARY
    print("\n" + "=" * 60)
    print("✅ PROOF COMPLETE!")
    print("=" * 60)
    print("\nWHAT CHANGED:")

    print("\n1. Hyperparameters:")
    if classifier_with_hyperparams.config:
        print("   ✓ Config was updated with optimal temperature, top_p, max_tokens")
    else:
        print("   ✗ No config changes (bug?)")

    print("\n2. Prompts/Demonstrations:")
    if fully_optimized.demo_manager and fully_optimized.demo_manager.demos:
        print(f"   ✓ Added {len(fully_optimized.demo_manager.demos)} few-shot examples")
    else:
        print("   ✗ No demonstrations added (bug?)")

    print("\n3. Test outputs:")
    print(f"   Initial: {test1.outputs}")
    print(f"   After hyperparams: {test2.outputs}")
    print(f"   After prompts: {test3.outputs}")

    # Save to prove persistence
    fully_optimized.save("proof_optimized.json")
    print("\n💾 Saved to proof_optimized.json - load it to see persistent changes!")

    # Load and verify
    loaded = Predict.load("proof_optimized.json")
    print("\n🔄 Loaded from file:")
    inspect_config(loaded, "LOADED")


if __name__ == "__main__":
    asyncio.run(main())
