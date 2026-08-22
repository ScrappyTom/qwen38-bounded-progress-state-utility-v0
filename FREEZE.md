# Freeze — bounded progress-state utility v0

Date: 2026-08-21

Status: Stage A implementation and offline preflight freeze.

## Boundary

- Donor commit: `6bed7b208174646b803405fdce1a83a9432fba88`.
- Cell: accumulated-focus effect case, seed 42.
- Exact actor packet: eight messages, 20,099 prompt tokens.
- Response reserve: 4,096 tokens.
- Headroom: 893 tokens.
- Current candidate:
  `38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6`.
- Historical action: exact `read_lines` 860–937 reread.
- Pending update: none.

## Stage A

Call C0 replays the byte-identical donor actor request. It must reproduce the
historical action byte-for-byte or the experiment stops.

If C0 passes, call M1 uses the same task/evidence/candidate messages under a
dedicated maintenance system. It emits only five plain-text progress fields.
Maximum completion is 384 tokens; acceptance is 1–256 exact tokens, normal
stop, complete nonempty fields, and no JSON/action/fence surface.

One attempt and zero retries. Maximum Stage-A calls: two.

## Treatment gate

No treated actor runs in Stage A. The maintenance output must be directly
audited, frozen without repair, and inserted into a canonical bound package.
Exact postproduction tokenizer preflight must prove a marginal increment <=700
tokens and treated headroom >=193 tokens under the unchanged 4,096-token actor
reserve.

## Claim limit

The selected history is known and only one trajectory qualifies. Expression,
behavioral salience, and utility remain separate. Any downstream effect belongs
to the complete package, including prose, binding, role, recency, and template
serialization.
