#!/usr/bin/env python3
"""Quick optimization demo - shows prompts and hyperparameters.

This is a simplified version that runs fast and shows:
1. How to set up optimization
2. The discovered prompt
3. The optimal hyperparameters
"""

import asyncio
import os

from logillm.core.predict import Predict
from logillm.optimizers import BootstrapFewShot
from logillm.providers import create_provider, register_provider


async def main():
    """Quick demo of optimization with visible results."""

    if not os.getenv("OPENAI_API_KEY"):
        print("Please set: export OPENAI_API_KEY=your_key")
        return

    print("=== LogiLLM Optimization Quickstart ===\n")

    # Setup
    provider = create_provider("openai", model="gpt-4.1-nano")
    register_provider(provider, set_default=True)

    # Create our analyzer (same as your example)
    analyzer = Predict("text -> sentiment: float, positives: list[str], negatives: list[str]")

    # More comprehensive training set with harder examples
    train_data = [
        # Very positive
        {
            "inputs": {
                "text": "The bartender was incredibly helpful and the beef wellington was to die for!"
            },
            "outputs": {
                "sentiment": 0.95,
                "positives": ["incredibly helpful bartender", "excellent beef wellington"],
                "negatives": [],
            },
        },
        {
            "inputs": {
                "text": "Absolutely phenomenal experience! The chef came out to greet us and the wine pairing was divine."
            },
            "outputs": {
                "sentiment": 0.98,
                "positives": ["phenomenal experience", "chef greeting", "divine wine pairing"],
                "negatives": [],
            },
        },
        # Very negative
        {
            "inputs": {"text": "Service was slow and the food was cold. Never coming back."},
            "outputs": {
                "sentiment": 0.1,
                "positives": [],
                "negatives": ["slow service", "cold food", "won't return"],
            },
        },
        {
            "inputs": {
                "text": "Worst meal I've had in years. Overpriced, underseasoned, and the waiter was rude."
            },
            "outputs": {
                "sentiment": 0.05,
                "positives": [],
                "negatives": ["worst meal", "overpriced", "underseasoned", "rude waiter"],
            },
        },
        # Mixed/nuanced - these are harder!
        {
            "inputs": {
                "text": "Great atmosphere but parking was terrible. Food was decent though nothing special."
            },
            "outputs": {
                "sentiment": 0.5,
                "positives": ["great atmosphere", "decent food"],
                "negatives": ["terrible parking", "nothing special"],
            },
        },
        {
            "inputs": {
                "text": "The appetizers were outstanding but the main course disappointed. Service tried their best despite being understaffed."
            },
            "outputs": {
                "sentiment": 0.6,
                "positives": ["outstanding appetizers", "service tried their best"],
                "negatives": ["disappointing main course", "understaffed"],
            },
        },
        {
            "inputs": {
                "text": "Beautiful interior and great cocktails, but the food took forever and was lukewarm when it arrived."
            },
            "outputs": {
                "sentiment": 0.4,
                "positives": ["beautiful interior", "great cocktails"],
                "negatives": ["food took forever", "lukewarm food"],
            },
        },
        # Subtle sentiment differences
        {
            "inputs": {
                "text": "Not bad, but I expected more given the reviews. The pasta was good at least."
            },
            "outputs": {
                "sentiment": 0.55,
                "positives": ["good pasta"],
                "negatives": ["expected more", "disappointing compared to reviews"],
            },
        },
        {
            "inputs": {
                "text": "Solid neighborhood spot. Nothing fancy but reliable and fairly priced."
            },
            "outputs": {
                "sentiment": 0.7,
                "positives": ["solid", "reliable", "fairly priced"],
                "negatives": [],
            },
        },
        {
            "inputs": {
                "text": "The view alone is worth it! Food was just okay but the sunset was spectacular."
            },
            "outputs": {
                "sentiment": 0.65,
                "positives": ["amazing view", "spectacular sunset"],
                "negatives": ["food just okay"],
            },
        },
    ]

    # Test input
    test_text = "The bartender was incredibly helpful and the beef wellington was to die for! I just wish they had more outdoor seating and closer parking."

    print("📊 BEFORE OPTIMIZATION:")
    print(f"Input: {test_text[:80]}...")
    result_before = await analyzer(text=test_text)
    print(f"Output: {result_before.outputs}\n")

    print("🔧 OPTIMIZING with BootstrapFewShot...\n")

    # Simple metric
    def sentiment_metric(pred, ref):
        if ref is None:
            return 0.5
        pred_val = float(pred.get("sentiment", 0.5))
        ref_val = float(ref.get("sentiment", 0.5))
        return max(0, 1 - abs(pred_val - ref_val))

    # Use BootstrapFewShot for quick optimization (adds examples)
    optimizer = BootstrapFewShot(
        metric=sentiment_metric,
        max_bootstrapped_demos=4,  # More examples now that we have more data
        max_labeled_demos=3,  # Include some labeled examples too
        max_rounds=2,  # Do a couple rounds of optimization
    )

    # Run optimization (fast!)
    result = await optimizer.optimize(module=analyzer, dataset=train_data)

    optimized = result.optimized_module

    print("✅ OPTIMIZATION COMPLETE!\n")

    # Show the prompt being used
    print("📝 FINAL PROMPT STRUCTURE:")
    print("  - Base signature: text -> sentiment, positives, negatives")
    if optimized.demo_manager and optimized.demo_manager.demos:
        print(f"  - Few-shot examples: {len(optimized.demo_manager.demos)} examples included")
        # Show more examples since we have them
        for i, demo in enumerate(optimized.demo_manager.demos[:4], 1):
            text = demo.inputs.get("text", "")[:40]
            sentiment = demo.outputs.get("sentiment", 0)
            print(f"    Example {i}: '{text}...' → {sentiment}")
    print()

    # Show hyperparameters (if modified)
    print("🎯 HYPERPARAMETERS:")
    if hasattr(optimized, "config") and optimized.config:
        print(f"  Config: {optimized.config}")
    else:
        print("  Using defaults (temperature=0.7, top_p=1.0)")
    print()

    # Test optimized version
    print("📊 AFTER OPTIMIZATION:")
    print(f"Input: {test_text[:80]}...")
    result_after = await optimized(text=test_text)
    print(f"Output: {result_after.outputs}\n")

    # Compare
    print("📈 COMPARISON:")
    print(f"  Before: sentiment={result_before.outputs.get('sentiment')}")
    print(f"  After:  sentiment={result_after.outputs.get('sentiment')}")
    print()

    # Test on validation examples to show improvement
    print("📊 VALIDATION on new examples:")
    validation_tests = [
        ("Incredible experience! Will definitely return!", 0.9),  # Should be very positive
        ("Terrible service, cold food, never again.", 0.1),  # Should be very negative
        ("Good but not great. Some hits and misses.", 0.5),  # Should be mixed
    ]

    total_error_before = 0
    total_error_after = 0

    for text, expected in validation_tests:
        before = await analyzer(text=text)
        after = await optimized(text=text)
        before_sent = float(before.outputs.get("sentiment", 0.5))
        after_sent = float(after.outputs.get("sentiment", 0.5))

        error_before = abs(before_sent - expected)
        error_after = abs(after_sent - expected)

        total_error_before += error_before
        total_error_after += error_after

        print(f"  '{text[:30]}...'")
        print(f"    Expected: {expected:.2f}")
        print(f"    Before:   {before_sent:.2f} (error: {error_before:.2f})")
        print(f"    After:    {after_sent:.2f} (error: {error_after:.2f})")

    avg_error_before = total_error_before / len(validation_tests)
    avg_error_after = total_error_after / len(validation_tests)
    improvement = ((avg_error_before - avg_error_after) / avg_error_before) * 100

    print(f"\n  Average error - Before: {avg_error_before:.3f}, After: {avg_error_after:.3f}")
    print(f"  Error reduction: {improvement:.1f}%")
    print()

    # For more advanced optimization, use HybridOptimizer:
    print("💡 TIP: For production, use HybridOptimizer to optimize both")
    print("   prompts AND hyperparameters simultaneously:")
    print()
    print("   from logillm.optimizers import HybridOptimizer")
    print("   optimizer = HybridOptimizer(metric=your_metric)")
    print("   result = await optimizer.optimize(module, dataset, param_space)")
    print()
    print("   This discovers the best temperature, top_p, AND prompt!")


if __name__ == "__main__":
    asyncio.run(main())
