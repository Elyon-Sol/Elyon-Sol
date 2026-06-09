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
   protocol was not completed. (In the Cowork sandbox, first rule out a
   mount/index artifact before assuming real corruption - see "Environment /
   sandbox recovery" at the end of this file.)

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

---

## Environment / sandbox recovery (Cowork)

Applies ONLY when running in the Cowork desktop sandbox - a Linux container
with this repo mounted from Windows. A native git checkout can ignore this
whole section. The mount is occasionally inconsistent; these rules keep a
session from mistaking an environment artifact for repository corruption, and
from leaving work in an un-pushable state. They encode the recovery used in
VL-069's resume (a corrupt index + stale lock from a prior crashed session).

1. Run all git from the sandbox shell, never the host file tools. Mount the
   folder first (request access if it is not connected).

2. Host vs sandbox truth. The host repo is the source of truth and is usually
   clean. If `git status` shows a dirty tree at resume, check whether the
   working files actually differ on the host before resolving - a "dirty" index
   with the files intact on disk is a mount/index artifact, not lost work.
   Rebuild the index from HEAD rather than discarding anything:
       GIT_INDEX_FILE=/tmp/ni git read-tree HEAD
       GIT_INDEX_FILE=/tmp/ni git update-index -q --refresh
       cp /tmp/ni .git/index

3. Deletes. The mount blocks unlink by default. If `rm` fails with "Operation
   not permitted", grant file-delete permission, then retry. Stale lock debris
   under `.git/` (`index.lock`, `*.stale`, `_swept_*`, `*.lock`) is safe to
   remove once delete is enabled.

4. Ghost entries. `.git/index.lock` and ref files can wedge: `stat`/`ls` report
   them present while `open`/`unlink` say they do not exist, and git reports
   "File exists" on lock creation. Do not trust their reported state. The host
   file tools' view is authoritative; a fresh Cowork session re-mounts and
   clears the cache.

5. Committing around a wedged lock. Never leave the tree dirty waiting on a
   lock. Stage through a sandbox-local index and build commits with plumbing
   (the .lock for /tmp lives on clean tmpfs):
       GIT_INDEX_FILE=/tmp/ix git read-tree HEAD
       GIT_INDEX_FILE=/tmp/ix git add <files>
       T=$(GIT_INDEX_FILE=/tmp/ix git write-tree)
       C=$(git commit-tree "$T" -p HEAD -m "<msg>")
       git update-ref refs/heads/main "$C"
   If `refs/heads/main` itself wedges, the commit objects are already safe -
   clear the ghost ref and write it fresh, then rebuild the index (rule 2):
       rm -f .git/refs/heads/main
       printf '%s\n' "$C" > .git/refs/heads/main
   For a build+close pair, chain a second commit with `-p "$C"` before the
   final update-ref.

6. Stat cache. If git does not notice edits made with the host file tools,
   `touch` the files before `git add`, or make the edits from the sandbox.
   (A stale cache can also serve OLD content to `git add`; after a host-tool
   edit, verify the sandbox sees it - `grep` for the new text - before commit.)

7. Push. The sandbox has no GitHub credentials and cannot push. Land every
   change as proper local commits (build + close per this protocol), verify
   clean (`git diff HEAD` empty, HEAD == origin/main locally), then hand the
   push to the author from a native terminal. A local commit that cannot be
   pushed leaves HEAD ahead of origin - close the push the same session so the
   at-rest invariant holds.

8. Prevention. Restarting Cowork before a session re-mounts the folder fresh
   and avoids most ghost-lock wedges.
