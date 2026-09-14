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
