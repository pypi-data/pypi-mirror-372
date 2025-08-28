#!/usr/bin/env python3
"""Simple optimization example with visible prompts and hyperparameters.

This demonstrates how LogiLLM's HybridOptimizer automatically discovers:
- The best prompt instructions
- Optimal few-shot examples
- Ideal hyperparameters (temperature, top_p)

All while showing you what it learned!
"""

import asyncio

# Enable detailed logging to see what's happening
import logging
import os
from typing import Any, Dict

from logillm.core.predict import Predict
from logillm.optimizers import HybridOptimizer
from logillm.providers import create_provider, register_provider

logging.basicConfig(level=logging.INFO, format="%(message)s")


async def main():
    """Optimize a sentiment analyzer and show the results."""

    if not os.getenv("OPENAI_API_KEY"):
        print("Please set: export OPENAI_API_KEY=your_key")
        return

    print("=== Simple Optimization Demo ===\n")

    # Setup provider (using smaller model for cost efficiency)
    provider = create_provider("openai", model="gpt-4o-mini")
    register_provider(provider, set_default=True)

    # Create a sentiment analyzer
    analyzer = Predict("text -> sentiment: float, positives: list[str], negatives: list[str]")

    # Training data with expected outputs
    train_data = [
        {
            "inputs": {
                "text": "The bartender was incredibly helpful and the beef wellington was to die for!"
            },
            "outputs": {
                "sentiment": 0.9,
                "positives": ["helpful bartender", "excellent beef wellington"],
                "negatives": [],
            },
        },
        {
            "inputs": {"text": "Service was slow and the food was cold when it arrived."},
            "outputs": {
                "sentiment": 0.2,
                "positives": [],
                "negatives": ["slow service", "cold food"],
            },
        },
        {
            "inputs": {"text": "Great atmosphere but parking was a nightmare. Mixed feelings."},
            "outputs": {
                "sentiment": 0.5,
                "positives": ["great atmosphere"],
                "negatives": ["parking problems"],
            },
        },
        {
            "inputs": {"text": "Absolutely perfect evening! Everything exceeded expectations."},
            "outputs": {
                "sentiment": 0.95,
                "positives": ["perfect evening", "exceeded expectations"],
                "negatives": [],
            },
        },
    ]

    # Test the baseline performance
    print("📊 TESTING BASELINE (no optimization):\n")
    test_text = "The view was spectacular but the prices were outrageous!"
    result = await analyzer(text=test_text)
    print(f"Input: '{test_text}'")
    print(f"Output: {result.outputs}\n")

    # Define what "good" means for our task
    def sentiment_accuracy(pred: Dict[str, Any], ref: Dict[str, Any]) -> float:
        """Score how close the prediction is to the reference."""
        if ref is None:
            return 0.5

        # Compare sentiment values (main metric)
        pred_sentiment = float(pred.get("sentiment", 0.5))
        ref_sentiment = float(ref.get("sentiment", 0.5))
        sentiment_diff = abs(pred_sentiment - ref_sentiment)
        sentiment_score = max(0, 1 - sentiment_diff)

        # Bonus for identifying correct positives/negatives
        pred_positives = set(pred.get("positives", []))
        ref_positives = set(ref.get("positives", []))
        pred_negatives = set(pred.get("negatives", []))
        ref_negatives = set(ref.get("negatives", []))

        # Simple overlap scoring
        pos_score = (
            len(pred_positives & ref_positives) / max(1, len(ref_positives))
            if ref_positives
            else 1.0
        )
        neg_score = (
            len(pred_negatives & ref_negatives) / max(1, len(ref_negatives))
            if ref_negatives
            else 1.0
        )

        # Weighted average (sentiment is most important)
        return 0.6 * sentiment_score + 0.2 * pos_score + 0.2 * neg_score

    print("🔧 OPTIMIZING (this takes ~30 seconds)...\n")

    # Create hybrid optimizer
    optimizer = HybridOptimizer(
        metric=sentiment_accuracy,
        strategy="alternating",  # Alternate between prompt and hyperparameter optimization
        num_candidates=3,  # Try 3 different variations
        max_iterations=2,  # Keep it quick for demo
    )

    # Define hyperparameter search space
    param_space = {
        "temperature": (0.1, 0.9),  # Lower for more consistent analysis
        "top_p": (0.5, 1.0),
    }

    # Run optimization
    result = await optimizer.optimize(module=analyzer, dataset=train_data, param_space=param_space)

    # Get the optimized module
    optimized_analyzer = result.optimized_module

    print("\n" + "=" * 50)
    print("✅ OPTIMIZATION COMPLETE!")
    print("=" * 50 + "\n")

    # Show discovered hyperparameters
    print("🎯 DISCOVERED OPTIMAL HYPERPARAMETERS:")
    if hasattr(optimized_analyzer, "config") and optimized_analyzer.config:
        for key, value in optimized_analyzer.config.items():
            if key in ["temperature", "top_p", "max_tokens"]:
                print(f"  {key}: {value}")
    print()

    # Show the optimized prompt (instruction)
    print("📝 OPTIMIZED PROMPT INSTRUCTION:")
    if hasattr(optimized_analyzer, "signature") and hasattr(
        optimized_analyzer.signature, "instructions"
    ):
        instructions = optimized_analyzer.signature.instructions
        if instructions:
            print(
                f"  '{instructions[:200]}...'" if len(instructions) > 200 else f"  '{instructions}'"
            )
    else:
        print("  (Using default instructions)")
    print()

    # Show selected few-shot examples
    print("📚 SELECTED FEW-SHOT EXAMPLES:")
    if optimized_analyzer.demo_manager and optimized_analyzer.demo_manager.demos:
        print(f"  Using {len(optimized_analyzer.demo_manager.demos)} examples")
        for i, demo in enumerate(optimized_analyzer.demo_manager.demos[:2], 1):
            text_preview = demo.inputs.get("text", "")[:50]
            sentiment = demo.outputs.get("sentiment", 0)
            print(f"  {i}. '{text_preview}...' → sentiment: {sentiment}")
    else:
        print("  No few-shot examples selected")
    print()

    # Test the optimized version
    print("📊 TESTING OPTIMIZED VERSION:\n")
    result_optimized = await optimized_analyzer(text=test_text)
    print(f"Input: '{test_text}'")
    print(f"Output: {result_optimized.outputs}\n")

    # Compare before and after
    print("📈 COMPARISON:")
    print(f"  Before: {result.outputs}")
    print(f"  After:  {result_optimized.outputs}")

    # Save the optimized model
    print("\n💾 Saving optimized model to 'sentiment_analyzer_optimized.json'...")
    optimized_analyzer.save("sentiment_analyzer_optimized.json")

    print("\n✨ Done! You can load and use the optimized model with:")
    print("   analyzer = Predict.load('sentiment_analyzer_optimized.json')")
    print("   result = await analyzer(text='Your text here')")


if __name__ == "__main__":
    asyncio.run(main())
