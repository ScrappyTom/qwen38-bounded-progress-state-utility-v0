# H05 bounded progress-state eligibility audit

Date: 2026-08-21

## Question

Does an existing measured boundary already contain stable exact evidence and
current candidate material while the actor nevertheless continues acquisition,
with no pending update and enough capacity for a bounded progress-state package?

This audit is mechanical and investigator-side. It does not claim that the
resident evidence is semantically sufficient for the entire task.

## Candidate review

| Candidate | Exact residency / behavior | Capacity | Disposition |
|---|---|---:|---|
| Exact-construction reentry, seed 42 | R033 reread was followed by a substantive mutation on the next call | 374 tokens before the mutating call | Exclude: control already transitions to action |
| Exact-construction reentry, seed 314159 | Actor requested nonresident R030 and its result could not be delivered | -716 prospective | Exclude: missing-evidence/delivery boundary |
| Recurrent exact-state observation case | Latest-update replacement repeatedly displaced prior observations | 282 tokens at the late repeat | Exclude: exact co-residency not stable and package cannot fit |
| Exact-workspace directory, observation case | Resident reread | 155 tokens | Exclude: insufficient package capacity |
| Exact-focus relocation, observation case | Demand moved to another resident span | 97 tokens | Exclude: insufficient package capacity |
| Accumulated focus, observation case | Demand expanded to nonresident lines 547–619 | 104 tokens | Exclude: missing exact material and insufficient package capacity |
| Passive model-managed residency | Pending-result control state became unreachable | -45 tokens | Exclude: control-plane reachability failure |
| Accumulated focus, effect case | Four exact governing documents, current patched candidate identity/suffix, R033, and a second model-selected exact focus are resident; actor rereads that second focus exactly | 893 tokens | **Eligible, conditional on package preflight** |

## Selected boundary

- Donor: `ScrappyTom/qwen38-accumulated-exact-focus-v0`
- Donor commit: `6bed7b208174646b803405fdce1a83a9432fba88`
- Run: `runs/2026-08-21-sealed-accumulated-exact-focus-v0`
- Cell: `02-effect-patch-s42`
- Request: `requests/call-01.json`
- Seed: 42
- Current candidate ID:
  `38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6`
- Current file SHA-256:
  `888c142abcad4c3bd9081960bdb18b7402be6415c03b456033ed3c7aed134d39`
- Control prompt: 20,099 tokens
- Frozen response reserve: 4,096 tokens
- Headroom: 893 tokens
- Historical action: `read_lines` 860–937
- Historical classification: exact reread of the just-delivered second focus
- Candidate changed by historical action: no
- Pending observation/effect before the call: none

The request has eight messages. The immediately preceding accepted focus result
is present as the final user message and has crossed the decision boundary.
The actor-visible standing state includes all four governing donor documents,
the current patched candidate binding and suffix, and both exact focus results.

## Qualification and limitation

This is the strongest available local boundary for H05 because the actor asks
for exact bytes already delivered through its own two-step focus selection.
It is not proof that the full task is semantically complete, and only one
trajectory qualifies. Any experiment is descriptive.

The actor treatment is eligible only if exact tokenizer preflight proves that
the complete progress-state package adds no more than 700 prompt tokens, leaves
at least 193 tokens beyond the unchanged response reserve, and changes no
existing message byte. If production, binding, or serialization exceeds that
limit, stop before actor inference.

## Decision

Proceed to one dedicated maintenance-expression call, one exact contemporaneous
control reproduction, and—only if both gates pass—a short treated actor
continuation. Do not add a second seed, remove resident evidence, shorten the
response reserve, or tune a failed note.
