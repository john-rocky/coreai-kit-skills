# CoreAIKit integration reference

These snippets follow the [0.4.1 README](https://github.com/john-rocky/coreai-kit/blob/0.4.1/README.md)
and [ChatDemo](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/ChatDemo).
For another version, read those paths at that version before adapting them.

## Package and first response

For an Xcode app, add `https://github.com/john-rocky/coreai-kit` with **Exact Version:
0.4.1** and select the **CoreAIKit** product. For a Swift package, add to the existing manifest:

```swift
.package(url: "https://github.com/john-rocky/coreai-kit", exact: "0.4.1")
// In the app target's dependencies:
.product(name: "CoreAIKit", package: "coreai-kit")
```

From an async throwing function:

```swift
import CoreAIKit

guard let modelID = ModelCatalog.builtin.entry(id: "qwen3-0.6b")?.modelID else {
    throw CoreAIKitError.modelNotAvailableOnPlatform(id: "qwen3-0.6b")
}
let chat = try await ChatSession(model: modelID)
for try await event in await chat.streamResponse(to: "What is the capital of Japan?") {
    if case .response(let delta) = event { print(delta, terminator: "") }
}
```

In SwiftUI, use the app's async flow with `do`/`catch`, update UI state on the main
actor, and display response deltas. Keep the session for a second turn. Qwen3 0.6B's
catalog lists approximately 352 MB on Mac and 456 MB on iPhone; allow at least 1 GB
free disk for this starter. These are download sizes.

The [setup and validation record](https://github.com/john-rocky/coreai-kit/blob/0.4.1/docs/GETTING_STARTED.md)
contains the tested beta toolchain and additional first-use/conversation checks.
Use a process-local `DEVELOPER_DIR` when selecting a second installed Xcode; an app
integration does not require changing the machine's global Xcode selection.

## Choose the example for the input and output

| Feature | Exact 0.4.1 source | API / distinction |
|---|---|---|
| Text chat | [ChatDemo](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/ChatDemo) | `ChatSession`; use the release's built-in model pin |
| FoundationModels interface | [README integration](https://github.com/john-rocky/coreai-kit/blob/0.4.1/README.md#use-your-model-with-foundationmodels) | `KitLanguageModel` with `LanguageModelSession` |
| Image + text | [VLChat](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/VLChat) | `KitVisionModel`; a chat-only bundle cannot accept images |
| Text to speech | [Speak](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/Speak) | `KitSpeaker`; returned PCM includes a sample rate |
| Specific speech recognizer | [Transcribe](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/Transcribe) | `KitTranscriber`; check preprocessing and the selected model |
| Entity extraction / PII redaction | [InfoExtract](https://github.com/john-rocky/coreai-kit/tree/0.4.1/Examples/InfoExtract) | `InformationExtractor` or `CoreAI.redact`; read its separate task setup |
| Task-level APIs | [Cookbook](https://github.com/john-rocky/coreai-kit/blob/0.4.1/docs/COOKBOOK.md) | `CoreAIOps`; some tasks route to Apple's system APIs |
| Typed decisions (System One shape), 0.5.0+ | [Decide](https://github.com/john-rocky/coreai-kit/tree/0.5.0/Examples/Decide) | `CoreAI.decide` / `TypedDecisions`; `decide-cli serve` for a `/v1/systemone` client, 16 options per choice |

The helper lists `catalog.json` entries only. Some task APIs have separate model
configuration; absence from this catalog does not establish that the entire task
is unsupported. Follow the task example before selecting a bundle.

## Source hierarchy

- Selected release README and validation record: dependency setup and tested scope.
- Selected release `catalog.json`: IDs, kinds, pins, platform paths/sizes.
- Selected task example and package source: input/output and lifecycle contracts.
- Individual Hugging Face model card and original license: model-specific terms.
- [Current Kit documentation](https://john-rocky.github.io/coreai-kit/llms.txt) and
  [zoo index](https://john-rocky.github.io/coreai-model-zoo/models/index.json): discovery;
  a live entry can differ from an older release.

Swift snippets are adapted from CoreAIKit by Daisuke Majima, BSD-3-Clause; see the
repository LICENSE. The skill does not redistribute model weights.
