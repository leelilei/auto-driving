"""Compatibility entry point for the repaired ChinaTravel integration runner.
Old B0/B1/B2 runs used incompatible schemas and are retired, not benchmark baselines.
Use: stage3_baseline_experiment.py run --config PATH --run-dir NEW_DIRECTORY
Or:  stage3_baseline_experiment.py replay --run-dir DIRECTORY
"""
from chinatravel_pipeline import main
if __name__ == '__main__':
    main()
