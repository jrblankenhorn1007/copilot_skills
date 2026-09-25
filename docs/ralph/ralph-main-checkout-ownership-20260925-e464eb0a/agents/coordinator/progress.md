# Coordinator progress - exclusive main ownership

## Iteration 1 - 2026-09-25

- **Run:** `copilot-skills-main-checkout-ownership-20260925-e464eb0a`.
- **Original fetched `origin/main`:** `ad4e663aa21259946ec112f7831b822529117b3b`.
- **Isolated branch/worktree:** `ralph/main-checkout-ownership-20260925-e464eb0a` /
  `/Users/jrblankenhorn/copilot_skills.worktrees/ralph-main-checkout-ownership-20260925-e464eb0a`.
- **Refresh:** Fetched `origin/main` without checking out or pulling shared
  `main`. Rebased this isolated branch first onto
  `e9fe3d175d1ca76b03fccdbe53431205b80e5c23` and then
  `20293c720b18a1a21ff150f566823493b7a2717d`, after the
  status-reporting agent signed out. The original publisher remained
  preserved on `preserve/local-main-05e3189-before-origin-refresh-20260925-0151`;
  only its released script and guide were imported, not its overlapping
  Ralph/dashboard changes.
- **Split:** One tightly coupled status-publisher/lease transaction and
  its Ralph instructions; no disjoint worker assignment was ready while
  another run owned the controlling Ralph files. No workers were launched
  or counted toward the requested default of two.

### Test-first evidence

| Slice | Exact command | Result |
|---|---|---|
| Entrypoint Red | `PYTHONDONTWRITEBYTECODE=1 python3 .github/skills/ralph-loop/tests/test_main_ownership_contract.py` | Expected failure: the agent, skill, and orchestration did not link a main sign-in, wait, or immediate release. |
| Publisher Red | `PYTHONDONTWRITEBYTECODE=1 python3 .github/skills/ralph-loop/tests/test_main_ownership_publisher.py` | Expected failure: a status commit had no preceding main claim/release, and a foreign owner was ignored. |
| Merge-result Red | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_release_rejects_a_result_from_before_main_signin` | Expected failure: a pre-sign-in SHA was accepted as a merge result. |
| Concurrency Red | `PYTHONDONTWRITEBYTECODE=1 python3 .github/skills/ralph-loop/tests/test_main_ownership_publisher.py` | Expected failure: simultaneous fetches in one Git directory contended on `refs/remotes/origin/main`; changed to per-process temporary fetch refs. |
| Retry-cost Red | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_idempotent_status_retry_does_not_reserve_main_or_push` | Expected failure: an unchanged status produced two unnecessary main commits. |
| Merge-signout Red | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_merge_cannot_be_signed_out_without_a_verified_result_commit` | Expected failure: a merge could be marked complete without a resulting SHA. |
| Fetch-recovery Red | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_transient_verification_fetch_failure_does_not_mislabel_published_status` | Expected failure with three interrupted verification fetches: an accepted status push was labeled failed. |
| Ref-cleanup Red | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_fetch_interruption_cleans_its_temporary_ref` | Expected failure: a temporary fetch ref remained after an interruption. |
| Concurrency Green | `cd .github/skills/ralph-loop/tests && for trial in 1 2 3; do PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_publisher.MainOwnershipPublisherTests.test_competing_agents_wait_until_recorded_owner_signs_out || exit 1; done` | Passed three repeated contention checks after unique-ref fetch and atomic push retry. |
| Documentation and runtime Green | `cd .github/skills/ralph-loop/tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_main_ownership_contract test_main_ownership_publisher test_multi_agent_contract` | Passed 35 tests in 58.357 seconds after the 20293c7 rebase. |
| Diff check | `git diff --check` | Passed for the current unstaged changes; repeat after staging all records. |

The runtime checks cover task sign-in remaining active after main sign-out,
status commits bracketed by ownership-only commits, concurrent contenders,
waiting for release, foreign release refusal, stale result rejection, merge
release verification, ambiguous push outcomes, failed release reporting,
idempotent retries, and preservation of the local main checkout.

### Current boundary - 2026-09-25T06:50:38Z

The status-reporting run released the agent/skill/orchestration paths, so the
new main protocol is wired there and the relevant contract suite is green.
The separate iteration-stall run still has an `IN_PROGRESS` task record
claiming `docs/ralph-status.md`, the root README, and the existing contract
test. Its dashboard scope is not edited here. This leaf and the coordinator
dashboard must be reconciled in one coordination cycle after that run signs
out. Until then, the implementation is not integrated on remote main, the
memory review is pending, and no completion marker is justified.
