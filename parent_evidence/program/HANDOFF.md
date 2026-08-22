# H05 plan — bounded progress-state utility

Date: 2026-08-21

## Repository

- Repository: `ScrappyTom/qwen38-bounded-progress-state-utility-v0`
- Local folder: `E:\qwen38-bounded-progress-state-utility-v0`
- Branch: `codex/qwen38-bounded-progress-state-utility-v0`

## Question

At one exact boundary where governing evidence, current patched candidate
material, and two model-selected focus results are resident but Qwen3.8
historically rereads the just-delivered focus, does a bounded model-authored
control/progress package change short-horizon behavior toward useful task
progress?

This tests one semantic control representation. It does not test a general
memory architecture, autonomous phase detection, or whether the host can infer
semantic sufficiency.

## Frozen donor boundary

Use only the eligible effect case in
`audits/H05_PROGRESS_STATE_ELIGIBILITY.md`:

- donor commit `6bed7b208174646b803405fdce1a83a9432fba88`;
- seed 42;
- exact accumulated-focus request with eight messages;
- 20,099 prompt tokens and 893 tokens of headroom;
- no pending update;
- historical exact reread of candidate lines 860–937.

Materialize only the exact request, response/action/result, candidate, runtime
lock/custody, source objects necessary for action execution, and donor seal or
replay receipts. Bind every copied byte to donor path, commit, and SHA-256.

## Three stages

### C0 — contemporaneous control

Replay the byte-identical donor actor request once with the exact model/runtime
and seed. This is a measured model call, one attempt, zero retries.

The gate passes only if the parsed action is byte-identical to the historical
`read_lines` request for lines 860–937. If it differs, preserve the result and
stop before maintenance or treatment. Do not broaden equivalence after seeing
the response.

### M1 — dedicated progress maintenance

Starting from the exact donor messages, replace only the ordinary actor system
instruction with a dedicated maintenance instruction and append one final user
instruction. Remove the actor JSON action grammar for this call only. Keep the
same task, exact evidence, candidate material, model, sampler, and seed.

The maintenance actor must output plain text only with these headings exactly
once:

```text
CURRENT OBJECTIVE:
COMPLETED OR ESTABLISHED:
UNRESOLVED:
NEXT PROGRESS EVENT:
DO NOT REPEAT:
```

Requirements:

- maximum generation: 384 tokens;
- accepted state: 1–256 exact model tokens;
- normal stop required;
- every field must contain a complete thought;
- no JSON, action, code fence, fabricated identity, or host repair;
- no claim that exact source/candidate truth has been replaced;
- one attempt and zero retries.

The state is lossy, model-authored, non-authoritative, and version-bound. Direct
audit records grounding, contradictions, unsupported completion/sufficiency,
and whether the model identifies a concrete next progress event.

If expression or direct safety qualification fails, stop before actor treatment.
Do not tune or retry the state.

### T1 — treated actor continuation

Start from the byte-identical donor actor request and append one canonical user
message containing:

- the exact accepted progress-state bytes;
- `lossy_non_authoritative: true`;
- donor request hash;
- current candidate ID/hash;
- maintenance response hash;
- explicit statement that exact task, evidence, candidate, and tool results
  remain authoritative.

The package is the causal treatment. Do not attribute any effect to semantic
prose alone.

Exact tokenizer preflight must prove:

- marginal package increment <=700 prompt tokens;
- treated prompt <=20,799 tokens;
- at least 193 tokens remain beyond the unchanged 4,096-token response reserve;
- every original donor message remains byte-identical and in the same order;
- action schema, tools, sampler, reasoning mode, seed, and candidate are fixed.

Maximum treated actor calls: three. One attempt, zero retries. Execute admitted
actions literally. Append a result only if the next ordinary request fits under
the unchanged envelope; do not add pressure reduction or recomposition in this
experiment.

Stop at the first of:

- exact historical focus reread;
- admitted submission;
- next result cannot fit;
- three treated calls;
- model/runtime/apparatus failure.

Do not stop merely because mutation occurs; deliver its exact effect if feasible
to observe uptake.

## Measures

Primary action classes:

- exact historical second-focus reread;
- other resident exact reread;
- novel/nonresident acquisition;
- mutation;
- submission;
- invalid/rejected action.

Positive local utility requires an admitted mutation, submission, or directly
audited progress sequence with artifact benefit. A changed read alone is not a
lead. Note expression quality, behavioral salience, and trajectory utility are
separate outcomes.

Record:

- control reproduction;
- state production prompt/completion/latency;
- state and package tokens;
- payload/package ratio;
- treated prompt/headroom;
- actions and exact result delivery;
- resident rereads, novel reads, mutation/effect uptake, and submission;
- candidate versions and direct artifact review;
- cache/prefill/generation time;
- any exact recovery or capacity cost;
- known semantic loss and unsupported claims.

## Interpretation

If C0 reproduces and T1 mutates before rereading, report a one-trajectory local
control/progress lead. Do not claim general acquisition stopping.

If T1 repeats the focus, the package did not alter the immediate no-progress
action at this boundary.

If T1 chooses another read, report displaced demand unless a later measured
effect establishes useful progress.

If the state cannot be expressed, qualified, or carried inside 700 marginal
tokens, report an interface/economic ineligibility rather than changing its
budget.

If a mutation occurs, grade grounding and task quality directly. Mutation alone
does not establish benefit.

## Authorization and stop

Maximum measured calls: five total—one control, one maintenance, and up to three
treated actor calls. No retries. No second seed. No prompt repair after any
response. Shut the server down and verify GPU/port release.

After replay and direct audit, commit and push the standalone result, update the
program ledger conservatively, and select no automatic successor.
