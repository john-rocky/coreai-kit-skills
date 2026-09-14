# CoreAIKit skills

Ask your coding agent to add a local model to an existing Swift app. The
`integrate-coreai` skill helps it select a CoreAIKit release, resolve the actual
model ID and device variant, wire the feature into the app, and handle the first
download and follow-up requests.

For example:

> Add local chat to this SwiftUI app using Qwen3 0.6B. Keep the response in the
> existing conversation view and show download and loading progress.

> Add an on-device text-to-speech action to this Mac app. Check the selected
> model's download size and return its PCM at the correct sample rate.

## Install

The [open skills CLI](https://github.com/vercel-labs/skills) can discover and install
the skill for your chosen agent. Run this from the **app project**:

```bash
npx skills add john-rocky/coreai-kit-skills --skill integrate-coreai
```

Select the agent you want in the installer, or pass `--agent codex` or
`--agent cursor`. The default scope is the current project. Preview without
installing:

```bash
npx skills add john-rocky/coreai-kit-skills --list
```

Review [SKILL.md](skills/integrate-coreai/SKILL.md) and its
[integration reference](skills/integrate-coreai/references/integration.md).
The skill guides app development; installing it does not install CoreAIKit,
download model weights, start inference, or modify global agent instructions.

## Resolve a model before writing Swift

The bundled Python helper fetches the **selected package release's** public
catalog and returns JSON. It needs Python 3.9+ and the standard library, with no
Python dependencies or API key. Metadata lookup works on non-Mac hosts too.

```bash
python3 skills/integrate-coreai/scripts/resolve_model.py \
  --release 0.4.1 --platform macos --id qwen3-0.6b
```

This resolves the `macos` variant at an immutable Hugging Face revision, with a
catalog download size of 352 MB. The iPhone variant is separately selected with
`--platform ios` and lists 456 MB. Unknown IDs and unavailable platforms fail
instead of silently selecting another bundle.

```bash
# Find chat models enrolled in the selected release for iPhone.
python3 skills/integrate-coreai/scripts/resolve_model.py \
  --release 0.4.1 --platform ios --kind chat

# Inspect explicitly live catalog data, which may differ from a release.
python3 skills/integrate-coreai/scripts/resolve_model.py \
  --release main --platform macos --kind tts
```

The reference starter is CoreAIKit **0.4.1**, with its published **Mac / Xcode 27
beta 5** validation. Model sizes and platform entries are catalog metadata, not
new hardware measurements or a GA guarantee. Follow the selected release's
requirements before building or running an app.

## Related resources

- [Try an app or choose a model](https://john-rocky.github.io/core-ai/)
- [CoreAIKit source and quickstart](https://github.com/john-rocky/coreai-kit)
- [Existing zoo conversion/reproduction skills](https://github.com/john-rocky/coreai-model-zoo#agent-skills)
- [Core AI Catalog](https://github.com/kevinqz/coreai-catalog): independent model discovery and MCP tools; its IDs are distinct from CoreAIKit's IDs.

This repository focuses on **consuming models in Swift apps**. It uses the existing
CoreAIKit catalog rather than maintaining a second copy or a new inference runtime.

## Validation and license

```bash
python3 -m unittest discover -s tests -v
```

The helper tests cover model identity, task filters, immutable pins, and platform
separation. They do not run a model. See [LICENSE](LICENSE) (BSD-3-Clause). Model
weights and upstream packages retain their own licenses. Community maintained by
Daisuke Majima; not affiliated with Apple.
