# Borrowing ledger

The standalone repository imports 21 exact files from two pinned, clean donors:

- `ScrappyTom/qwen38-accumulated-exact-focus-v0` at
  `6bed7b208174646b803405fdce1a83a9432fba88` supplies the exact boundary,
  candidate, four source objects, runtime lock/custody, result audit, replay,
  and seal.
- `ScrappyTom/bounded-context-experimental-program` at
  `5ee502ada15e9a1abc012fa1ea3b1ff59a251c38` supplies the H05 eligibility
  audit and experiment contract.

Every copied object retains donor path, commit, SHA-256, copied path, copied
SHA-256, size, and byte-equivalence in
`PARENT_MATERIALIZATION_RECEIPT.json`. Copied evidence remains donor evidence.
