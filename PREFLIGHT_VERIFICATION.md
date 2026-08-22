# Offline preflight verification

- 21 imported donor/program files are byte-equivalent.
- The eight-message control packet reconstructs exactly.
- Exact control prompt: 20,099 tokens; headroom: 893.
- Maintenance prompt: 18,745 tokens with a 384-token generation reserve;
  headroom: 5,959.
- Representative state: 93 tokens.
- Representative complete package increment: 300 prompt tokens.
- Representative treated headroom: 593 tokens.
- The measured package remains subject to <=700 marginal tokens and >=193
  treated headroom after production.
- No chat completion occurred during preflight.
- CPU tokenizer server stopped and released its port.
- Focused tests: 8/8 passed before freeze.
