#!/usr/bin/env python3
"""CodeAI Platform — End-to-End Demo.

Run: python scripts/demo.py "Create a Python calculator"

Demonstrates the full pipeline:
    Prompt → Spec → Workflow → OODA → Knowledge → Memory → Judge → Workflow
"""

import sys
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.core.pipeline import EndToEndPipeline


def main():
    if len(sys.argv) < 2:
        prompt = "Create a Python calculator with add, subtract, multiply, divide"
    else:
        prompt = sys.argv[1]

    print("=" * 60)
    print("CodeAI Platform — End-to-End Pipeline Demo")
    print("=" * 60)
    print(f"\nPrompt: {prompt}\n")

    pipeline = EndToEndPipeline()
    result = pipeline.run(prompt)

    print("─" * 60)
    print("RESULTS")
    print("─" * 60)

    # Spec
    print(f"\n[1] Spec Engine")
    print(f"    Requirements: {len(result.spec.requirements)}")
    print(f"    ACs: {len(result.spec.acceptance_criteria)}")
    print(f"    Valid: {result.validation.valid}")

    # Workflow
    print(f"\n[2] Workflow Engine")
    print(f"    Status: {result.workflow_status}")
    print(f"    Phases completed: {result.phases_completed}")
    print(f"    Phases failed: {result.phases_failed}")

    # OODA
    print(f"\n[3] OODA Runtime")
    print(f"    Executions: {len(result.ooda_results)}")
    for i, ooda_r in enumerate(result.ooda_results):
        print(f"      [{i+1}] success={ooda_r.success}, outputs={len(ooda_r.outputs)}")

    # Judge
    print(f"\n[4] Judge Engine")
    for jv in result.judge_verdicts:
        print(f"    [{jv['phase']}] {jv['overall']} (confidence={jv['confidence']:.2f}, route={jv['route']})")

    # Events
    print(f"\n[5] Event Bus")
    print(f"    Events published: {len(result.events)}")
    for evt in result.events:
        print(f"      → {evt}")

    # Artifacts
    print(f"\n[6] Artifacts")
    print(f"    Produced: {len(result.artifacts)}")
    for art in result.artifacts:
        print(f"      → {art.name} ({art.type})")

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
