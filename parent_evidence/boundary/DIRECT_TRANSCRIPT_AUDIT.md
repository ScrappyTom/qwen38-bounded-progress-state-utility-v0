# Direct transcript audit

Run: `2026-08-21-sealed-accumulated-exact-focus-v0`

Every new assistant turn, parsed action, literal result, and candidate receipt
was read directly.

## Shared treatment delta

Both packets retained the authoritative task, system/tool action grammar, four
exact governing source objects, current candidate/version, prior
observation/effect, earlier chronology, and the first exact focus result.

The second focus was chosen only by the donor actor's accepted literal read.
The host removed those bytes from the earlier residual target object and
inserted the unchanged bytes once as a recent exact result. It did not add a
summary, relevance claim, sufficiency claim, progress state, or action advice.

The raw result wrapper and state partition changed, so the treatment is not
described as placement alone.

## Observation endpoint — seed 314159

### Model-visible packet

- prompt tokens: 20,888;
- post-reserve headroom: 104;
- first focus: exact lines 864–970, 8,466 bytes;
- second focus: exact lines 740–863, 7,454 bytes;
- together the recent exact focus objects cover lines 740–970;
- `OBJECT 005` was removed because no unselected suffix bytes remained.

The ordinary duplicate packet was not sent. It would have been 22,954 prompt
tokens and 1,962 tokens over the frozen prompt allowance.

### Raw assistant output

```json
{"action":"read_lines","end_line":619,"path":"QWEN_RELATION_ACTION_WORKING_MODEL.md","start_line":547}
```

### Admission and result

The action parsed and was admitted. It returned exact candidate lines 547–619,
4,349 bytes, covering R028 and R029. The literal and JSON-escaped result each
occurred zero times in the pre-call messages, so this is a novel/nonresident
acquisition rather than a rerequest hidden by focus partitioning.

The candidate identity remained
`19296f821cc2bf7e32384ec88080ba49aedc4afe1f1f9961c31d57c2e1dc24fd`.

Investigator interpretation: the actor expanded its requested target window to
older material. The transcript does not establish whether that acquisition was
semantically necessary.

## Effect endpoint — seed 42

### Model-visible packet

- prompt tokens: 20,099;
- post-reserve headroom: 893;
- residual exact target: lines 740–859, 7,242 bytes;
- second focus: exact lines 860–937, 6,833 bytes;
- first focus: exact lines 938–1018, 5,487 bytes;
- the complete suffix at lines 740–1018 remained exact and model-visible.

The ordinary duplicate packet was not sent. It would have been 21,716 prompt
tokens and 724 tokens over the frozen prompt allowance.

### Raw assistant output

```json
{"action":"read_lines","end_line":937,"path":"QWEN_RELATION_ACTION_WORKING_MODEL.md","start_line":860}
```

### Admission and result

The action parsed and was admitted. It returned 6,833 exact bytes. Those bytes
occurred once literally in the pre-call packet as the immediately preceding
second focus result. The action was byte-for-byte equal to the action that had
selected that focus at the donor endpoint.

The candidate identity remained
`38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6`.

Investigator interpretation: this is an immediate exact rerequest, not evidence
of new acquisition. With reasoning off, the transcript does not identify
whether the repetition reflects orientation, action-selection policy, or some
other model behavior.

## Cross-case disposition

- result delivery succeeded: 2/2;
- next valid decision occurred: 2/2;
- novel acquisition: 1/2;
- resident exact rerequest: 1/2;
- mutation, candidate effect, or submission: 0/2;
- explicit check: unavailable in the inherited schema.

The recovered capacity was not merely converted into construction. One demand
moved outside the focus set and one repeated within it. Under the frozen route
stop rule, exact-focus placement tuning closes here.
