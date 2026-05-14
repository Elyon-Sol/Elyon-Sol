# Elyon-Sol - Session Protocol

How to start and end a working session so repository continuity holds.
This file exists because no model (Claude, Grok, or otherwise) carries
memory between sessions. The repository is the continuity layer; this
protocol is how a session connects to it.

---

## RESUME PROTOCOL - run at the start of every session

Do these in order before any new work. If working with a model, paste
the OUTPUT of these steps into the session - do not summarize them.

1. Pull and check state:
       git pull origin main
       git log --oneline -10
       git status
   Confirm: working tree clean, up to date with origin. If not, resolve
   that first - a dirty tree from a prior session means the prior close
   protocol was not completed.

2. Read STATE.md in full. It is the entry point. Specifically:
   - "Current verified state" - what is true now
   - "Next open action" - the ordered starting point
   - "Known open gaps" - the full gap list

3. Read the tail of the verification ledger:
       cat EVIDENCE/verification_ledger.md
   Read at minimum the last 2-3 entries. This tells you what was most
   recently verified and how.

4. If working with a model: give it the primary sources for whatever
   the Next-open-action requires - not summaries, not this conversation's
   history, not prior model output. Scope the task to those sources
   explicitly (per VL-008: task-to-source binding is what makes a model's
   work valid).

5. State the session's goal in one sentence before starting. It should
   map to an item in STATE.md's "Next open action". If it does not,
   either STATE.md is stale or the goal is scope creep - resolve which.

---

## CLOSE PROTOCOL - run at the end of every session

Do these in order before stopping. A session is not complete until
these are done - an incomplete close breaks the next resume.

1. Commit all working changes. No uncommitted work survives a session
   in a trustworthy form. If something is not ready to commit, it is not
   done - note it in STATE.md as in-progress rather than leaving it loose.

2. Update STATE.md:
   - "Last updated" line - date and last ledger entry
   - "Current verified state" - reflect anything verified this session
   - "Next open action" - re-order or rewrite so the FIRST item is
     literally the next thing to do. This is the single most important
     field for continuity.
   Commit the STATE.md update as its own commit.

3. If any claim was verified, corrected, retracted, or disputed this
   session: append a ledger entry. Verification work that is not
   ledgered did not, for continuity purposes, happen.

4. Push:
       git log --oneline origin/main..HEAD   # confirm what will push
       git push origin main
       git log --oneline -5                  # confirm origin matches HEAD

5. Confirm the close is clean:
       git status        # must be: clean, up to date with origin
   If git status is not clean and synced, the close protocol is not
   complete. Finish it before stopping.

---

## The invariant

At rest - between sessions - the repository must satisfy:
- working tree clean, HEAD == origin/main
- STATE.md's "Next open action" first item is literally the next task
- the verification ledger reflects all verification work to date

If a resume protocol finds these untrue, the previous session's close
protocol failed. Fixing that is the first task of the new session,
before anything else.
