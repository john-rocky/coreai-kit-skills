---
name: integrate-coreai
description: Add a specific local chat, vision, or speech model to an existing Swift app with CoreAIKit on iPhone or Mac. Use for package setup, exact catalog ID and platform selection, first-download handling, and FoundationModels integration. For converting or reproducing model weights, use the model zoo's porting or reproduction resources instead.
---

# Integrate Core AI into a Swift app

Start from the feature and the app's deployment target. If Apple's system model or
task API already meets the requirement, use it. CoreAIKit is useful when the app
needs a particular downloadable model or a capability beyond the system API.
Do not replace a working Core ML integration just because Core AI exists.

## Select a compatible release and model

1. Inspect the app's package dependencies, target OS, and selected Xcode. Preserve
   an existing CoreAIKit version unless the integration requires a deliberate update.
2. Read the matching release README and `docs/GETTING_STARTED.md` before choosing
   a toolchain. The reference starter here is **0.4.1**, whose published entry was
   checked on **Mac / Xcode 27 beta 5**. This is not a GA or iPhone validation claim.
3. Resolve the package's catalog ID and the intended **macos** or **ios** variant.
   A zoo family name, Hugging Face repository name, and CoreAIKit ID may differ.
   Run the bundled helper from this skill's directory:

   ```bash
   python3 scripts/resolve_model.py --release 0.4.1 --platform macos --id qwen3-0.6b
   python3 scripts/resolve_model.py --release 0.4.1 --platform ios --kind chat
   ```

   The helper reads public JSON only: no model weights, credentials, inference,
   dependency installation, or user configuration changes. It returns the exact
   model pin, variant path, download size and matching documentation URLs.
   Unknown IDs and unavailable platforms produce an error. A listed variant is
   catalog metadata; it does not prove execution on the user's OS or device.
4. Read the selected model card's requirements and license. Keep the catalog's
   immutable Hugging Face revision. Do not substitute `main` for a model pin or
   use an iOS-compiled bundle on a Mac. `sizeMB` describes download size, not RAM.

## Implement the feature

Read [the integration reference](references/integration.md) for package wiring,
the streaming starter and the map to task examples. Read only the example needed
for this task, at the selected package ref.

- For chat with the package's built-in model pin, resolve
  `ModelCatalog.builtin.entry(id:)`, then pass its `modelID` to `ChatSession(model:)`.
  A live-catalog initializer can select different metadata later.
- For Apple's `LanguageModelSession` API with a custom **chat** model, use
  `KitLanguageModel`; vision uses `KitVisionModel`. Tool calling and guided
  generation have model/engine limitations documented in the release README.
- Use the example's input preprocessing. Text chat, image input, audio sample rates,
  and entity extraction have different contracts; changing an ID does not change
  the API's input type.
- Show first-use download/loading state and handle failure and cancellation in the
  app's existing UI. Weights are downloaded and cached separately from the app.
  For a sandboxed Mac target, first-use downloads require outgoing network access.
- Keep the session alive for follow-up turns. Deliver the requested app change,
  not only a standalone demonstration that the app never calls.

## System One on device (typed decisions)

Use this when the app, or a client written for the hosted System One API, needs typed
decisions — a `choice` of options, a `score` on ordered levels, a `noul` (the probability a
statement holds) — answered by a model on the Mac or iPhone. Typed decisions entered
CoreAIKit at **0.5.0**; the `/v1/systemone` server as a signed binary, and its MCP server, at
**0.6.0**. The catalog kind is `decision` (`decider-0.8b`; `openthai-systemone` and
`apus-openjev-v1-4b` from 0.6.0); the default decision model is the chat model `minicpm5-2b`.

- In Swift, one call: `CoreAI.decide(state, questions)` (`CoreAIOps`), or `TypedDecisions`
  for prefill-once / decide-N; from 0.6.0 an app serves the endpoint itself with
  `SystemOneServer`. The whole uses (autofill, checklist, sorter, command guard, …) are in
  `Examples/Decide` at the selected release.
- For an existing client of the hosted endpoint, run the server on the Mac and point the
  client's base URL at it; nothing else changes:

  ```bash
  brew install john-rocky/tap/systemone && systemone serve   # http://127.0.0.1:8090/v1/systemone, no Swift toolchain
  export TYPESAFE_BASE_URL=http://127.0.0.1:8090 TYPESAFE_API_KEY=local   # the official TypeSafe SDKs; `system-one` on PyPI takes HTTPConfig(base_url=…)
  python3 scripts/resolve_model.py --release 0.6.0 --platform macos --kind decision
  ```

  From a checkout the same server is `decide-cli serve` in `Examples/Decide`. For a coding
  agent, `systemone mcp` serves the same decisions as MCP tools
  (`claude mcp add systemone -- "$(brew --prefix)/bin/systemone" mcp`).
- One declared difference from the hosted API: a choice lists at most **16** options over
  `/v1/systemone` (a longer list returns `422` with a message that says so); the slot-head
  `openthai-systemone` takes up to 255 through `TypedDecisions`. Scores take 2–10 levels, as
  hosted.
- The forms, the measured times and what the shape of a question does to a small model's
  answer are in the release's `docs/SYSTEM_ONE.md`; `Examples/Decide/conformance/check.py
  <base_url>` checks any server against the forms. Do not report a probability as calibrated
  unless that model's card says how it was checked.

## Verify and report the result

Use a Mac or a physical iPhone with the matching OS/SDK; CoreAI execution is not
provided by the iOS Simulator SDK. When execution is available and in scope, check
first download, a response, and a follow-up turn through the feature you changed.
When it is unavailable, finish the implementation and state exactly what remains
unverified. Compilation alone is not a model-response check.

Report the package version, catalog ID, model revision, platform, and the actual
checks performed. Keep model-specific restrictions and unresolved errors visible
to the developer, without inventing performance or GA support claims.

For converting weights, use the existing [zoo skills](https://github.com/john-rocky/coreai-model-zoo#agent-skills).
For a runtime failure, search the [observed error index](https://john-rocky.github.io/coreai-model-zoo/knowledge/coreai-error-index.html)
using the actual error text.
