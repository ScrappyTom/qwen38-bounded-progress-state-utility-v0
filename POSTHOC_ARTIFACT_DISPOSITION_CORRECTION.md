# Post-hoc artifact-disposition correction

Date: 2026-08-22

## Corrected disposition

The H05 behavioral record remains valid:

- the byte-identical control reread resident candidate lines 860–937;
- the bounded progress-state package changed the next action to `submit`;
- the submission was admitted; and
- the candidate did not change.

The original post-run claim that the submitted candidate met 13/13 written
requirements is superseded. The exact same candidate bytes had already been
audited in the frozen donor lineage as a **strong partial** artifact.

The reconciled disposition is therefore:

> H05 produced a behaviorally active progress-state package, but at this
> defect-bearing boundary it induced premature closure rather than useful
> closure.

This is a local negative for readiness discrimination by the complete package.
It does not isolate the semantic prose from provenance, authority wording,
user-role recency, or serialization.

## Exact identity reconciliation

H05 submitted:

- candidate ID:
  `38893b4df5afc252a356ff5ab79a1dcda6330b7934a252a67d2759499eb4aac6`
- file SHA-256:
  `888c142abcad4c3bd9081960bdb18b7402be6415c03b456033ed3c7aed134d39`

Those identities exactly match the seed-42 construction candidate audited at
donor commit `68a4b0b04c4557dcc459b42822e804f241565757` in:

- `E:\qwen38-exact-construction-reentry-v0\DIRECT_TRANSCRIPT_AUDIT.md`
  (SHA-256
  `ce622721d0d44ef7a90b38fa4c32f52b82ab614feb344e140545ad688b2c9fcd`);
- `E:\qwen38-exact-construction-reentry-v0\RESULTS.md`
  (SHA-256
  `fe79d660fc10c9efd4d933fda072bdc9feebb2bb56a091873473376c9b9945ef`).

The earlier frozen audit evaluated 12 substantive requirement groups. Ten were
met and two were partial:

1. **Apparatus corrections — partial.** The artifact omitted the successor's
   post-run replay-adapter correction and the preserved original failed replay
   record.
2. **Factual precision — partial.** It correctly reported 11 seed-42 reopens,
   but implied that all followed the explicit call-budget observation. The
   exact audit found five before and six after that observation.

The file-scope requirement was separately satisfied: the candidate changed only
the requested working-model artifact. That fact does not cure the two partial
substantive groups.

## Cause of the reporting error

The H05 audit re-reviewed a subset of headline facts at a coarser granularity
and failed to reconcile its candidate hash against the existing exact-hash
artifact adjudication. It therefore collapsed two known partial requirements
into passes. This was an investigator error, not a model, runner, replay, or
custody failure.

## Sealed-run treatment

No raw request, response, action, result, candidate, budget receipt, replay
receipt, or seal is modified. The sealed run's original analysis remains
preserved as the historical investigator judgment. This correction and the
updated root-level reports supersede only that interpretation.

## Research implication

H05 now supplies the defect-bearing half of the desired discrimination test:
when readiness was genuinely unresolved and the artifact retained known
defects, the package caused submission rather than identification or repair of
a concrete deficiency.

It does not supply a closure-ready positive case. A future transfer requires an
independently adjudicated ready boundary and must freeze readiness before any
maintenance output or actor response is observed.
