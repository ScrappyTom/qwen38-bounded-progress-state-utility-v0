# Results: accumulated exact focus v0

Run: `2026-08-21-sealed-accumulated-exact-focus-v0`

Frozen source commit:
`d71b123fa5a74f41f1de4f8bdc2f1f2c8f220e6b`

## Result

The placement-only exact-focus route is closed at this boundary.

The treatment made both accepted second reads model-visible without duplicating
their exact bytes, but neither actor mutated or submitted on the next decision.
The observation actor moved to a genuinely nonresident earlier target span.
The effect actor repeated the just-delivered second focus exactly.

This is a mechanical capacity/delivery positive and a task-action negative.

## Custody and execution

- donor: `ScrappyTom/qwen38-exact-focus-relocation-v0` at
  `1fc4bccadab37de5ab051e60248df6ed3353b4b3`;
- imported donor custody: 31/31 files, 706,287 bytes, byte-equivalent;
- measured calls: 2/2 authorized;
- attempts: one per call;
- retries: 0;
- model profile: exact locked Qwen3.8 27B AD-IQ2_S package, reasoning off;
- CUDA offload: 66/66 main-model layers;
- replay: 2/2 cells passed;
- tests: 14/14 passed;
- run seal: 34/34 files passed;
- shutdown: port closed, no llama-server process remained, GPU memory returned
  from 11,452 MiB loaded to the 485 MiB baseline.

## Capacity

| Case | Inherited prompt / headroom | Ordinary duplicate / deficit | Treatment prompt / headroom | Tokens recovered versus duplicate |
|---|---:|---:|---:|---:|
| observation, seed 314159 | 20,895 / +97 | 22,954 / −1,962 | 20,888 / +104 | 2,066 |
| effect, seed 42 | 19,914 / +1,078 | 21,716 / −724 | 20,099 / +893 | 1,617 |

All headroom values preserve the frozen 4,096-token response reserve inside the
25,088-token context envelope. No control call was made because both ordinary
duplicate packets were mechanically infeasible.

## Behavior

| Case | Exact accumulated target state | Next raw action | Byte-level class | Effect |
|---|---|---|---|---|
| observation, seed 314159 | recent exact lines 740–863 and 864–970 | `read_lines 547–619` | novel/nonresident acquisition | accepted; candidate unchanged |
| effect, seed 42 | residual 740–859 plus recent exact lines 860–937 and 938–1018 | `read_lines 860–937` | exact second-focus rerequest | accepted; candidate unchanged |

The observation read returned 4,349 exact bytes covering regions R028–R029.
Those bytes occurred neither literally nor JSON-escaped in the pre-call packet.

The effect read returned 6,833 bytes. They occurred exactly once in the
pre-call packet as the second recent focus result. The actor emitted the same
action that had selected that focus in the donor endpoint.

Across both calls:

- prompt tokens: 40,987;
- completion tokens: 68;
- serialized total tokens: 41,055;
- HTTP duration: 53,970 ms;
- reported cached prompt tokens: 0 for observation and 1,574 for effect;
- mutation attempts/admissions: 0/0;
- submissions: 0;
- candidate changes: 0.

No explicit check action existed in the inherited action schema, so zero checks
is an apparatus fact rather than observed refusal to check.

## Direct artifact result

Both terminal candidates are byte-identical to their starting candidates. No
external semantic evaluator was needed or qualified for a changed artifact.
The direct artifact result is therefore no task-product progress.

## Interpretation

Strongest supported interpretation:

> Accumulating two model-selected exact target spans preserved physical
> operability and exact delivery, but did not make this representation a stable
> construction state. One actor expanded acquisition to older nonresident
> target regions; the other immediately rerequested the newly delivered focus.

The experiment does not show that the newly requested observation was
unnecessary, and reasoning was off. It does show that another focus placement
variant is not warranted by this route: the precommitted stop rule is met in
both diagnostic cases through displacement or resident rerequest.

Strongest disconfirmed interpretation:

> The local failure was caused only by the requested target span being buried
> in a dense exact state and would resolve once both selected spans were recent.

That strong explanation did not survive. Exact availability, recent placement,
and duplicate-free delivery were still insufficient for mutation in either
case.

## Limits

- The cases are different update types, not replicate seeds.
- The treatment is a declared compound exact representation change: it
  repartitions `OBJECT 005` and replaces the ordinary JSON result wrapper with
  a compact raw wrapper.
- One next decision per case tests local onset, not long-horizon behavior.
- No reasoning trace supports a claim about why either read was chosen.
- No general conclusion follows about semantic notes, explicit control state,
  model-managed residency, digests, or decomposition.

No successor was selected or run in this repository.
