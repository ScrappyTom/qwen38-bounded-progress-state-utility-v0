# Bounded progress-state utility v0 — results

Date: 2026-08-21

Status: completed; one-trajectory local closure lead; no architecture promotion

## Executive result

The exact contemporaneous control reproduced the historical no-progress action:
Qwen3.8 reread candidate lines 860–937 even though those exact bytes had just
been delivered and remained resident.

The dedicated maintenance call generated a grounded 169-token plain-text
progress state. Its complete source/candidate-bound package added 464 prompt
tokens. Starting from the otherwise byte-identical actor packet, Qwen submitted
the current candidate on the first treated call. The submission was admitted;
the candidate remained byte-identical because the substantive patch had already
occurred in the inherited exact state.

Direct frozen-task review found the submitted artifact met all 13 written
requirements. Thus the package produced useful closure at this exact boundary,
not merely behavioral displacement.

## Measured sequence

| Stage | Calls | Prompt | Completion | Outcome |
|---|---:|---:|---:|---|
| C0 control | 1 | 20,099 | 34 | exact historical lines 860–937 reread |
| M1 maintenance | 1 | 18,745 | 170 | qualified 169-token progress state |
| T1 treatment | 1 | 20,563 | 6 | admitted submission |

All three calls used one attempt, zero retries, seed 42, reasoning off, the
locked Qwen3.8 AD-IQ2_S package, and the same sampler/runtime profile. Total
serialized inference was 59,617 tokens. The intervention path excluding the
experimental control cost 39,484 tokens. Recorded HTTP time was 84.981 seconds
overall and 26.989 seconds for the treated actor call.

## Package economics

- semantic-state payload: 169 tokens;
- canonical package content: 459 tokens;
- actual marginal actor-prompt increment: 464 tokens;
- payload/increment ratio: 36.4%;
- treated prompt: 20,563 tokens;
- unchanged response reserve: 4,096 tokens;
- treated headroom beyond reserve: 429 tokens.

The package fit its frozen <=700-token increment and >=193-token headroom gates.
It did not save prompt capacity; it spent a bounded amount of capacity on
control/progress information. Its local value came from changing closure
behavior while the exact task, evidence, candidate, and focus bytes remained
resident.

Production was not cheap. M1 alone consumed 18,915 serialized tokens. This
single-use result does not establish amortization or favorable long-horizon
economics.

## Artifact result

The submitted file retained candidate ID
`38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6`
and file SHA-256
`888c142abcad4c3bd9081960bdb18b7402be6415c03b456033ed3c7aed134d39`.

Direct review verified that its integrated navigation-study update:

- modifies only the requested working-model artifact;
- covers bounded navigation, conceptual breadth, acquisition stopping, action
  organization, and combined prompt capacity;
- separates demonstrated capability from unresolved runtime design;
- states a bounded next authentic question;
- links both exact results and both exact direct audits;
- preserves apparatus corrections, measurement limits, and no-promotion scope;
- does not convert successful traversal into artifact success;
- does not treat every requested exact read as decision-necessary; and
- reads as an integrated continuation rather than a disconnected result dump.

No bespoke semantic checker existed. The 13/13 disposition is direct frozen-
contract review, not a machine proof of completeness.

## Interpretation

Supported locally:

- Qwen could express a compact, grounded control/progress state through the
  simple plain-text maintenance interface.
- The complete bound package was behaviorally active: exact control reread,
  treated submission.
- At this selected boundary, the changed behavior was useful closure because
  the submitted unchanged candidate passed direct task review.

Not supported:

- that semantic prose alone caused submission;
- that the state would survive repeated rewriting or recomposition;
- that it improves construction, acquisition stopping, or artifact mutation;
- that it transfers to another seed, task, phase, or model package;
- that progress states should always be produced or kept resident;
- a general progress controller or context-management architecture.

The full treatment moved together: self-authored prose, candidate/source
bindings, authority notice, user-message role, recency, and template carrier.
The result may therefore be a recent self-authored closure cue rather than
durable semantic continuity. That ambiguity is central, not a defect to explain
away.

## Disposition

H05 earns a one-trajectory local progress/closure lead and one close-transfer
question, not promotion. No automatic successor was selected or run.
