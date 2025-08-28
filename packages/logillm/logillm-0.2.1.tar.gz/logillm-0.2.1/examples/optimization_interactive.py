#!/usr/bin/env python3
"""Interactive optimization demo for Python notebooks/REPL.

Copy and paste these snippets into your Python session to see:
- How optimization improves results
- The final optimized prompt
- The discovered hyperparameters

Perfect for iPython, Jupyter, or just experimenting!
"""

# Cell 1: Setup

from logillm.core.predict import Predict
from logillm.optimizers import HybridOptimizer
from logillm.providers import create_provider, register_provider

# Setup provider (one time)
provider = create_provider("openai", model="gpt-4o-mini")
register_provider(provider, set_default=True)

# Cell 2: Create and test base analyzer
analyzer = Predict("text -> sentiment: float, positives: list[str], negatives: list[str]")

# Test it
result = await analyzer(
    text="The bartender was incredibly helpful and the beef wellington was to die for! "
    "I just wish they had more outdoor seating and closer parking."
)
print("BEFORE optimization:")
print(f"  Sentiment: {result.outputs.get('sentiment')}")
print(f"  Positives: {result.outputs.get('positives')}")
print(f"  Negatives: {result.outputs.get('negatives')}")

# Cell 3: Prepare training data
train_data = [
    {
        "inputs": {"text": "Amazing food and service! Best meal ever!"},
        "outputs": {
            "sentiment": 0.95,
            "positives": ["amazing food", "great service"],
            "negatives": [],
        },
    },
    {
        "inputs": {"text": "Terrible experience. Food was cold and overpriced."},
        "outputs": {
            "sentiment": 0.1,
            "positives": [],
            "negatives": ["terrible experience", "cold food", "overpriced"],
        },
    },
    {
        "inputs": {"text": "Good food but very slow service and noisy environment."},
        "outputs": {
            "sentiment": 0.5,
            "positives": ["good food"],
            "negatives": ["slow service", "noisy"],
        },
    },
]


# Cell 4: Define optimization metric
def sentiment_accuracy(pred, ref):
    """Score based on how close sentiment values are."""
    if ref is None:
        return 0.5
    pred_val = float(pred.get("sentiment", 0.5))
    ref_val = float(ref.get("sentiment", 0.5))
    diff = abs(pred_val - ref_val)
    return max(0, 1 - diff)


# Cell 5: Run optimization (this is where the magic happens!)
print("\n🔧 Optimizing... (takes ~20 seconds)")

optimizer = HybridOptimizer(
    metric=sentiment_accuracy,
    strategy="alternating",  # Try both prompt and hyperparameters
    num_candidates=2,  # Quick demo
    max_iterations=1,  # Just one round for demo
)

# Define search space for hyperparameters
param_space = {
    "temperature": (0.1, 0.7),  # Lower = more consistent
    "top_p": (0.8, 1.0),
}

result = await optimizer.optimize(module=analyzer, dataset=train_data, param_space=param_space)

optimized = result.optimized_module
print("✅ Optimization complete!")

# Cell 6: Show what was learned
print("\n📚 OPTIMIZATION RESULTS:")
print("-" * 40)

# Show hyperparameters
if hasattr(optimized, "config") and optimized.config:
    print("Discovered Hyperparameters:")
    for key in ["temperature", "top_p"]:
        if key in optimized.config:
            print(f"  {key}: {optimized.config[key]:.2f}")

# Show few-shot examples
if optimized.demo_manager and optimized.demo_manager.demos:
    print(f"\nSelected {len(optimized.demo_manager.demos)} few-shot examples:")
    for i, demo in enumerate(optimized.demo_manager.demos[:3], 1):
        text = demo.inputs.get("text", "")[:50] + "..."
        sentiment = demo.outputs.get("sentiment", 0)
        print(f"  {i}. '{text}' → {sentiment}")

# Show improvement
print(f"\nOptimization Score: {result.score:.2%}")

# Cell 7: Test the optimized version
result_opt = await optimized(
    text="The bartender was incredibly helpful and the beef wellington was to die for! "
    "I just wish they had more outdoor seating and closer parking."
)
print("\nAFTER optimization:")
print(f"  Sentiment: {result_opt.outputs.get('sentiment')}")
print(f"  Positives: {result_opt.outputs.get('positives')}")
print(f"  Negatives: {result_opt.outputs.get('negatives')}")

# Cell 8: Save the optimized model
optimized.save("my_optimized_analyzer.json")
print("\n💾 Saved to 'my_optimized_analyzer.json'")
print("Load it later with: Predict.load('my_optimized_analyzer.json')")

# Cell 9: Quick comparison on new text
test_texts = [
    "Absolutely perfect in every way!",
    "Disappointing and overpriced.",
    "Good but could be better.",
]

print("\n📊 COMPARISON on new examples:")
print("-" * 50)
for text in test_texts:
    before = await analyzer(text=text)
    after = await optimized(text=text)
    print(f"'{text}'")
    print(f"  Before: {before.outputs.get('sentiment'):.2f}")
    print(f"  After:  {after.outputs.get('sentiment'):.2f}")
    print()

# Cell 10: Understanding the optimization
print("💡 What happened during optimization?")
print("-" * 40)
print("1. HybridOptimizer tested different prompts")
print("2. It also tried different temperature/top_p values")
print("3. It measured which combination worked best")
print("4. The final model uses:")
print("   - Optimal hyperparameters for consistency")
print("   - Best few-shot examples from training data")
print("   - Improved internal prompting")
print("\n🚀 Result: Better, more consistent predictions!")
