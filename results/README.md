# Results Folder

This folder stores all results from agent evaluations, benchmarks, and submissions.

## Folder Structure

```
results/
├── benchmarks/           # Benchmark results against baselines
│   ├── benchmark_YYYYMMDD.md
│   └── ...
├── scores/           # Leaderboard scores from Kaggle submissions
│   ├── score_YYYYMMDD.md
│   └── ...
└── submissions/       # Archived submission files and notes
    ├── submission_v1/
    ├── submission_v2/
    └── ...
```

## How to Add Results

### Benchmarks
Add a new markdown file in `benchmarks/` with:
- Date
- Opponent(s)
- Win rate
- Average score
- Observations

### Scores
Add a new markdown file in `scores/` with:
- Date
- Submission version
- Kaggle leaderboard score
- Rank (if available)
- Notes on strategy changes

### Submissions
Create a folder for each submission with:
- Submission file(s)
- Description of strategy
- Score achieved
