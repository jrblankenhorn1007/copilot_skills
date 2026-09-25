we need a skill in our ralph loop pipeline that synchronizes all agents running. the way we do this, with a file on the remote git. in the docs folder. this is where the agents can communicate with each other to undersand the status. each agent that is running must sign into the codebase by committing that its about to work on something, state its task, record the prompt it used, the model, thinking effort, context, the works. worktree info and branch info important too. make it sorted in folders, and make sure the agents in the pipeline all know how to interface with this system. the intention to prevent merging/worktree issues. this file or set of files is basically the "sign in sign out" for "im editing this and here's what im doing"

i think its important that for this pipeline we allow the agents to bypass the normal pull request protocol to commit status updates to communicate with each other. no reviews. no worktree. no branches. direct commit to main on the status. communication needs to be very fast.

if gh is unavailable, thats a problem we need to fix. make sure gh is a dependency and installed per our docs. update them if needed.

finish the synchronization task first, then address that.

i need you to finish this task manually and commit directly to main.