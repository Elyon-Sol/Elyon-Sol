# canon.md  -  Transcription Verification Report (Rev. 2)

**Task:** Transcribe `Whitepaper_0_9_8_4_CANON_-_.pdf` to `canon.md`.
**Treated as:** a verification event, not a blind conversion.

**Rev. 2 changes:** F3 (notation) **decided and closed**  -  ASCII-safe, as a representation
choice. F1/F2 (numbering gaps) **decided**  -  locked as-is, corrections deferred to a future
canon-version event. `canon.md` regenerated in ASCII-safe form with a transcription note.

**Status of `canon.md`:** still SINGLE-SOURCE. It becomes canonical only after you verify
the remaining flagged points (F4, F5, F6) against the PDF and a ledger entry (VL-006)
records the verification with a hash.

---

## What was transcribed

All 10 PDF pages, all sections: Abstract, section 1-section 15, Appendix D (D.2, D.3, D.4). Section
numbering, headings, and structure preserved as in the source.

## Faithful  -  content preserved

- All section text is verbatim from the PDF (whitespace/line-wrap normalized only).
- Mathematical relations preserved in ASCII-safe form (see F3, now CLOSED).
- The section 6 pseudocode is preserved in a code block with original logic and indentation.
- Bullet lists and definition blocks preserved.

---

## CLOSED items

### F3  -  Notation: Unicode vs ASCII  -  CLOSED
**Decision:** ASCII-safe forms, treated as a **representation choice, not a content change.**
- `AC^3` / `T^26` for the superscript designations; `S_t`, `S_{t+1}`, `d_{t+1}`,
  `u_{t+1}`, `c_{t+1}` for subscripts; `<=>`, `->`, `AND`, `superset-or-equal`, `!=` for
  relational symbols.
- Rationale: byte-stable hashing and identical behavior across all editors, diffs, and
  terminals  -  required for a file that will be SHA256-locked. Per section 3 the notation is
  *nominal* (not mathematical exponents), so ASCII forms denote the identical constructs.
- A **Transcription Note** is included at the top of `canon.md` stating this explicitly, so
  the choice can never be mistaken for a silent canon edit. The note itself is marked
  "not canonical content."
- **Verification note:** an automated non-ASCII byte check (`grep -nP '[^\x00-\x7F]'`) was
  run against `canon.md` after generation. It caught em-dash characters (U+2014) remaining
  in section headings and definition lines  -  the math notation had been converted but the
  em-dashes had not. These were replaced with ` - ` (ASCII hyphen) and the check re-run;
  `canon.md` is now confirmed pure ASCII. This is logged here because the check doing its
  job  -  catching a missed character before lock  -  is exactly the verification process
  working as intended, and the next reviewer should know the file passed this check.
- This decision must be recorded in VL-006.

### F1 / F2  -  Section numbering gaps (section 8 has no 8.3; Appendix D has no D.1)  -  DECIDED
**Decision:** v0.9.8.4 is locked **as-is**, including these gaps. They are now known,
recorded properties of the canonical version  -  not defects to be fixed in place. Any
correction is a future canon-version event (new version, new hash, new lock, ledger entry).
- `canon.md` reproduces the gaps faithfully; nothing was renumbered or completed.
- This decision must be recorded as its own ledger entry (proposed **VL-007**), so it is
  durable beyond this session.
- It also establishes a governance rule for the maintenance protocol: **canon is corrected
  only by version increment, never by in-place edit.**

---

## STILL FLAGGED  -  you must check these against the PDF

### F4  -  The section 3 Notation Clarification is load-bearing  -  verify exactly
section 3 states the superscripts "are not mathematical exponents." This sentence governs how the
whole document is read, and it now also justifies the F3 ASCII decision. Read it in both the
PDF and `canon.md` side by side.

### F5  -  section 12.3 and section 13 are the G0 sections  -  verify character by character
G0 (the anchor gap) turns on the exact wording of section 12.3 (`CCS(S_t, S_{t+1}, I) = 1 iff...`)
and section 13 (`G(I) = AC^3(I) AND T^26(I) AND CCS(S_t, S_{t+1}, I)` plus "Eligibility does not
persist across state transitions without revalidation"). The entire envelope spec
(Deliverable 05) derives from these exact sentences. Verify section 12.1-section 12.4 and section 13 against the
PDF with extra care  -  checking that the ASCII rendering preserved the meaning, not just the
symbols.

### F6  -  Normalization I applied: "ElyonSol" -> "Elyon-Sol"
The PDF showed "ElyonSol" (no hyphen) at one line-wrap boundary in the Abstract  -  a likely
PDF line-break artifact. `canon.md` uses "Elyon-Sol" throughout (the correct form everywhere
else in the document). This is a normalization I made. If you want `canon.md` to be a *pure*
transcription including artifacts, revert it; if you want it readable, leave it. Minor, but
it is a change I made and you should confirm it.

---

## What I did NOT do

- Did not correct, complete, or renumber any canon content. F1/F2 reproduced as-is.
- Did not change canonical meaning  -  F3 is encoding only, with the equivalence documented.
- Did not add a hash. `canon.lock` is a separate step, after your verification.
- Did not touch the PDF. It remains the immutable source of record.

---

## Proposed next steps (in order)

1. **You verify** F4, F5, F6 against the PDF. F5 is the critical one.
2. Place in repo: `CANON/canon_v0.9.8.4.pdf` (immutable source) + `CANON/canon.md`
   (verified transcription).
3. Generate `CANON/canon.lock`  -  `sha256sum canon.md`  -  only after step 1.
4. Ledger entry **VL-006**  -  canon.md transcribed from canon_v0.9.8.4.pdf; F3 decided
   (ASCII representation choice); F4/F5/F6 verified by [you]; locked at [hash]; commit [hash].
5. Ledger entry **VL-007**  -  v0.9.8.4 known canonical properties: section 8 numbering gap (no 8.3),
   Appendix D gap (no D.1); decision: locked as-is, corrections deferred to future
   canon-version event.
6. Maintenance protocol gains the rule: **canon is corrected only by version increment.**

Until VL-006, `canon.md` is a candidate, not the canon.
