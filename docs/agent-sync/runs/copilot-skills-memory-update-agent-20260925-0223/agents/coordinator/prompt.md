Fix Ralph Loop's premature-stop behavior when a required post-merge Project
Memory review cannot start because shared Resource Manager capacity is
unavailable. Preserve the dedicated updater, complete handoff, verified-merge,
and atomic reservation requirements. Add a failing contract test first, then
document that the review remains PENDING and the run remains nonterminal; do
not substitute coordinator self-review or record NO_UPDATE. Continue safe
serial work, do not busy-poll or dispatch without a reservation, and use
ask_user to request a capacity remedy if no safe work remains. On each user
resume, refresh the complete live-session inventory and reserve a slot before
invoking the updater exactly once. Do not edit categorized memory; include any
durable lesson as a structured handoff for the dedicated updater. Keep branch,
progress, decision, and dashboard records synchronized.
