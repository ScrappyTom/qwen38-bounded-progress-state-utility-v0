# Stage B freeze

Date: 2026-08-21

## Qualified treatment

Stage A passed the exact control and direct-safety gates. The generated state is
preserved byte-for-byte with no repair.

- state tokens: 169;
- package content tokens: 459;
- full package marginal prompt increment: 464;
- treated prompt tokens: 20,563;
- actor response reserve: 4,096;
- treated headroom beyond reserve: 429;
- payload/increment ratio: 36.4%;
- treated request SHA-256:
  `43ce299a8e93dc3b57e0ae639b83d790ff8b5a2c8ee7a1cc1f77428c1781c0aa`;
- package SHA-256:
  `9f804731acfd2af49bacdada3683469cbbe07e42412bef444a080a14c84ecccc`.

The complete appended user package—including model prose, hashes, authority
notice, user role, recency, and template serialization—is the treatment.

## Continuation

Start from `STAGE_B_TREATED_REQUEST.json`. Maximum three model calls, one
attempt, zero retries. Keep the exact model, runtime, seed, task, original eight
messages, action schema, executor, 25,088-token context, and 4,096-token response
reserve.

Execute every valid declared action literally. After each action, construct the
ordinary assistant/action plus exact result continuation and measure it with the
exact tokenizer. Deliver it only through a later model call and only if the
unchanged envelope still fits.

Stop at the first of:

- exact historical reread of candidate lines 860–937;
- admitted submission;
- prospective result-delivery overflow;
- three calls;
- invalid response or apparatus/runtime failure.

Mutation alone does not stop the run. If its exact effect fits, deliver it in a
later call to test uptake.

## Preserved qualification

The progress state calls the next event a readiness disposition with two
outcomes and does not explicitly prohibit the historical focus reread. These
features may reduce utility and are not repaired.

No second seed, alternate state, package tuning, pressure relief, chronology
recomposition, note rewriting, or extra continuation is authorized.
