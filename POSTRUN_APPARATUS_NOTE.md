# Post-run apparatus note

- Standalone source freezes: `fc1727b4d8b1be7b21ce450cb325218bfeefcd8f`
  for Stage A and `dfeb411d711fb65913828ef065561e944926df63` for
  Stage B.
- Execution commits: `3497839a1932577251e058c057772006c857f60e`
  and `86f8aedfb29f93193ed971052e049f598d4dcd87`.
- Runtime: llama.cpp `b10434-7e4c0a968`, 25,088 context, q8 KV,
  reasoning off, 66/66 layers offloaded.
- Model SHA-256:
  `d416fa422c9035605c778f60d90a94b288c38b4f9ec2126b58ef938ce8d5f716`.
- Calls: three total, one attempt each, zero retries.
- Stage A replay: 18/18 checks passed.
- Stage B replay: 9/9 checks passed.
- Stage A run seal verified before Stage B freeze.
- Both servers stopped; port 18080 closed; GPU memory returned to the pre-run
  538 MiB baseline after each measured stage.

The CPU tokenizer projection performed only template/tokenization calls. It
made no chat completion and released its port.

The inherited action catalog's prose mentions a check operation, but the actual
declared response schema exposes no check action. Therefore checks were not an
available behavioral option in this experiment.

No host semantic repair, result retry, prompt edit after outcome, added seed,
or unplanned model call occurred.
