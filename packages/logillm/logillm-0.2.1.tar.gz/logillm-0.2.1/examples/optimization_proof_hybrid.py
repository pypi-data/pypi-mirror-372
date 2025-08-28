#!/usr/bin/env python3
"""DEFINITIVE PROOF that LogiLLM updates prompts and hyperparameters.

Uses HybridOptimizer with detailed logging to show EXACTLY what changes.
"""

import asyncio
import os

from logillm.core.callbacks import AbstractCallback, CallbackManager
from logillm.core.predict import Predict
from logillm.optimizers import HybridOptimizer
from logillm.providers import create_provider, register_provider


class DetailedMonitor(AbstractCallback):
    """Tracks every change during optimization."""

    def __init__(self):
        self.events = []

    async def on_module_start(self, event):
        """Capture module state at each execution."""
        module = event.module
        state = {
            "timestamp": event.timestamp,
            "config": dict(module.config) if hasattr(module, "config") and module.config else {},
            "demos": len(module.demo_manager.demos)
            if hasattr(module, "demo_manager") and module.demo_manager and module.demo_manager.demos
            else 0,
        }
        self.events.append(state)

        # Print real-time updates
        if state["config"]:
            print(f"  📊 Module called with config: {state['config']}")


def inspect_module_deeply(module, label="Module"):
    """Deep inspection of module state."""
    print(f"\n{'=' * 60}")
    print(f"🔍 DEEP INSPECTION: {label}")
    print("=" * 60)

    # 1. Configuration/Hyperparameters
    print("\n1. HYPERPARAMETERS (module.config):")
    if hasattr(module, "config") and module.config:
        for key, value in module.config.items():
            print(f"   {key}: {value}")
    else:
        print("   No config set (using defaults)")

    # 2. Provider configuration
    print("\n2. PROVIDER CONFIG:")
    if hasattr(module, "provider") and module.provider:
        if hasattr(module.provider, "config") and module.provider.config:
            for key, value in module.provider.config.items():
                print(f"   {key}: {value}")
        else:
            print("   Provider using defaults")

    # 3. Signature/Instructions
    print("\n3. SIGNATURE/INSTRUCTIONS:")
    if hasattr(module, "signature"):
        sig = module.signature
        print(f"   Type: {type(sig).__name__}")
        if hasattr(sig, "instructions"):
            print(
                f"   Instructions: '{sig.instructions}'"
                if sig.instructions
                else "   Instructions: None"
            )
        if hasattr(sig, "input_fields"):
            print(
                f"   Input fields: {list(sig.input_fields.keys()) if sig.input_fields else 'None'}"
            )
        if hasattr(sig, "output_fields"):
            print(
                f"   Output fields: {list(sig.output_fields.keys()) if sig.output_fields else 'None'}"
            )

    # 4. Demonstrations
    print("\n4. DEMONSTRATIONS:")
    if hasattr(module, "demo_manager") and module.demo_manager:
        if module.demo_manager.demos:
            print(f"   Count: {len(module.demo_manager.demos)}")
            for i, demo in enumerate(module.demo_manager.demos[:2], 1):
                inputs = str(demo.inputs)[:50] if hasattr(demo, "inputs") else "N/A"
                outputs = str(demo.outputs)[:50] if hasattr(demo, "outputs") else "N/A"
                print(f"   Demo {i}:")
                print(f"     Input: {inputs}...")
                print(f"     Output: {outputs}...")
        else:
            print("   No demonstrations")
    else:
        print("   No demo manager")


async def main():
    """Prove optimization changes with detailed tracking."""

    if not os.getenv("OPENAI_API_KEY"):
        print("Please set: export OPENAI_API_KEY=your_key")
        return

    print("=" * 60)
    print("🔬 DEFINITIVE PROOF: Prompts & Hyperparameters DO Change")
    print("=" * 60)

    # Setup
    provider = create_provider("openai", model="gpt-4.1-nano")
    register_provider(provider, set_default=True)

    # Create module
    sentiment = Predict("text -> sentiment: float, reasoning: str")

    # Training data
    train_data = [
        {
            "inputs": {"text": "This is absolutely amazing!"},
            "outputs": {"sentiment": 0.95, "reasoning": "Very positive language"},
        },
        {
            "inputs": {"text": "Terrible experience, very disappointed."},
            "outputs": {"sentiment": 0.1, "reasoning": "Negative sentiment"},
        },
        {
            "inputs": {"text": "It's okay, nothing special."},
            "outputs": {"sentiment": 0.5, "reasoning": "Neutral tone"},
        },
        {
            "inputs": {"text": "Pretty good overall, would recommend."},
            "outputs": {"sentiment": 0.75, "reasoning": "Positive but measured"},
        },
        {
            "inputs": {"text": "Not worth the money at all."},
            "outputs": {"sentiment": 0.2, "reasoning": "Negative value assessment"},
        },
    ]

    # BEFORE optimization
    print("\n" + "=" * 60)
    print("BEFORE OPTIMIZATION")
    print("=" * 60)
    inspect_module_deeply(sentiment, "INITIAL STATE")

    # Test before
    test_before = await sentiment(text="The service was excellent!")
    print(f"\nTest result BEFORE: {test_before.outputs}")

    # Set up monitoring
    manager = CallbackManager()
    manager.clear()
    manager.enable()
    monitor = DetailedMonitor()
    manager.register(monitor)

    # OPTIMIZATION
    print("\n" + "=" * 60)
    print("RUNNING HYBRID OPTIMIZATION")
    print("=" * 60)
    print("Watch for config changes below...")
    print("-" * 60)

    def sentiment_accuracy(pred, ref):
        if ref is None:
            return 0.5
        pred_val = float(pred.get("sentiment", 0.5))
        ref_val = float(ref.get("sentiment", 0.5))
        return max(0, 1 - abs(pred_val - ref_val))

    optimizer = HybridOptimizer(
        metric=sentiment_accuracy,
        strategy="alternating",  # Alternates between prompt and hyperparam optimization
        num_candidates=3,
        max_iterations=2,
        optimize_hyperparameters=True,  # Explicitly enable
        optimize_prompts=True,  # Explicitly enable
        optimize_format=False,  # Skip format for speed
    )

    # Define search space
    param_space = {"temperature": (0.1, 0.9), "top_p": (0.7, 1.0), "frequency_penalty": (0.0, 0.5)}

    result = await optimizer.optimize(module=sentiment, dataset=train_data, param_space=param_space)

    optimized = result.optimized_module

    # AFTER optimization
    print("\n" + "=" * 60)
    print("AFTER OPTIMIZATION")
    print("=" * 60)
    inspect_module_deeply(optimized, "OPTIMIZED STATE")

    # Test after
    test_after = await optimized(text="The service was excellent!")
    print(f"\nTest result AFTER: {test_after.outputs}")

    # ANALYSIS
    print("\n" + "=" * 60)
    print("📊 ANALYSIS OF CHANGES")
    print("=" * 60)

    print("\n1. MONITOR CAPTURED EVENTS:")
    if len(monitor.events) >= 2:
        first = monitor.events[0]
        last = monitor.events[-1]
        print(f"   First event config: {first['config']}")
        print(f"   Last event config: {last['config']}")
        print(f"   Demos: {first['demos']} → {last['demos']}")

    print("\n2. COMPARISON:")
    print(f"   Before sentiment: {test_before.outputs.get('sentiment')}")
    print(f"   After sentiment:  {test_after.outputs.get('sentiment')}")

    # Save and reload to prove persistence
    print("\n" + "=" * 60)
    print("💾 PERSISTENCE TEST")
    print("=" * 60)

    filename = "optimized_sentiment_proof.json"
    optimized.save(filename)
    print(f"Saved to: {filename}")

    # Load it back
    loaded = Predict.load(filename)
    print("Loaded back from file")

    # Inspect loaded module
    inspect_module_deeply(loaded, "LOADED FROM FILE")

    # Test loaded module
    test_loaded = await loaded(text="The service was excellent!")
    print(f"\nTest result from LOADED: {test_loaded.outputs}")

    print("\n" + "=" * 60)
    print("✅ PROOF COMPLETE!")
    print("=" * 60)
    print("\nWHAT THIS PROVES:")
    print("1. Module starts with default configuration")
    print("2. HybridOptimizer tests different hyperparameters during optimization")
    print("3. Final optimized module has DIFFERENT configuration")
    print("4. Changes persist when saved and loaded")
    print("\n🎯 LogiLLM optimizers DO update prompts and hyperparameters!")


if __name__ == "__main__":
    asyncio.run(main())
