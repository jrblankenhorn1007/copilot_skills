Replay the effective eight-agent Resource Manager change from PR #6 onto a
fresh branch based on the latest fetched origin/main, preserving the published
source branch and avoiding force-pushes. Keep the configured total limit at
eight including the coordinator, retain the degraded and critical live-pressure
guards, and keep RAM/CPU estimates diagnostic. Update branch-local Ralph and
decision records, run the targeted Resource Manager and relevant regression
checks, obtain independent Code and Security reviews for exact PR SHAs, and
merge only after repository gates pass. Verify the resulting commit on fetched
origin/main. Do not modify other active sessions' worktrees.
