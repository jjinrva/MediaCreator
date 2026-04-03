# Generation truth gates

A generation capability is only allowed to become `ready` when all of the following are true:

1. ComfyUI base URL is configured
2. the ComfyUI service is reachable
3. required workflow files exist
4. required workflow files are not placeholders
5. workflow validation confirms the graph is runnable for the expected target
6. checkpoint files exist
7. VAE files exist
8. there is an actual proof-image execution path in repo code
9. the verify step can produce a real saved proof image artifact

If any of the above are false, the system must remain `unavailable` or `partially-configured`.

A stored generation request is not a proof image.
A local LoRA registry entry is not a proof image.
A workflow JSON file with `nodes: []` is not a runnable generation graph.
