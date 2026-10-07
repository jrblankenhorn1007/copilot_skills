---
name: create-image
description: Generate or edit Runecore game-art images with the existing Runecore asset pipeline. Use when asked to create an image, sprite, portrait, icon, tile, or other visual asset for Runecore; do not use for image-processing-only or renderer-code changes.
---

# Create an image for Runecore

Use Runecore's existing `runecore_asset_pipeline` CLI for model-backed image generation. Do not replace it with direct API calls or a second provider client.

## Confirm the project and destination

1. Resolve the Runecore repository root from the current workspace or the user's stated path. Confirm it contains `src/asset_pipeline/AssetPipeline.cpp` and `docs/asset_generation_pipeline.md`. If there is no accessible Runecore checkout, ask for its path instead of guessing.
2. Read `docs/asset_generation_pipeline.md` and any relevant entity documentation and existing `request.json`. Keep the request's documented asset category, entity, label, style, provenance, and output layout.
3. Use the user's image description as the prompt. For a new request, include the asset's associated Markdown path in `documentation`, use an ID that includes the label, and make the request's `label` match its output directory. Enemy assets include a biome directory: `assets/generated/enemies/<biome>/<entity>/<label>/`. Other categories use `assets/generated/<category>/<entity>/<label>/`.
4. Set the prompt, output aspect ratio, presentation tier, and transparency from the request. Preserve supplied reference images and set `reference_image` only when the user asks to use one; verify that it exists relative to the Runecore root. The pipeline defaults to `runecore_hybrid_v1`, pixel presentation, and a transparent background. Its width and height select a supported model aspect ratio; they do not request an exact pixel output size.
5. Check for both `request.json` and `source.png` before writing or generating. The CLI writes to `source.png` and can replace an existing file. Never overwrite an existing request or image without the user's explicit confirmation; use a new asset directory when appropriate.

## Protect credentials and user data

The existing pipeline reads `OPENAI_API_KEY` from the process environment or the Runecore macOS Keychain entry. Never ask the user to paste a key into chat, put a key in `request.json`, pass it as a command-line argument, or include it in logs or Ralph records. If no credential is available, explain the supported secure options; do not run the interactive `configure` command without the user's approval.

Image generation sends the prompt and any reference image to OpenAI and may incur provider charges. A direct user request to generate an image authorizes one generation. Do not make extra variants unless requested.

## Generate and validate

Run commands from the Runecore repository root. Build the CLI if it is missing:

```sh
cmake --build build --target runecore_asset_pipeline
```

Generate the image and validate the resulting PNG:

```sh
./build/runecore_asset_pipeline generate assets/generated/<category>/<entity>/<label>/request.json
./build/runecore_asset_pipeline validate assets/generated/<category>/<entity>/<label>/source.png
```

For enemies, include the biome path shown above. Use the real, repository-relative paths and quote shell arguments when needed. The default pipeline model is `gpt-image-1`. The `validate` command checks the PNG signature; it does not judge visual quality. Confirm the output exists, inspect it when an image viewer is available, and report any quality check that was not performed. Do not change the runtime manifest, approve the art, or commit generated output unless the user asks.

If generation or validation fails, report the failed command and the actionable error without exposing credentials. Do not report success until the output exists and validation passes.

## Tests

From the `copilot_skills` repository root, run the offline skill contract test:

```sh
python3 .github/skills/create-image/tests/test_create_image_skill.py
```

The same file contains an opt-in live-model integration test. It calls the Runecore CLI once, validates the generated PNG, and deletes its temporary request and image. Because it calls the real image API, it is skipped unless explicitly enabled and may incur a provider charge. Set `RUNECORE_ROOT` to the Runecore checkout; credentials must already be available through the environment or Keychain:

```sh
RUN_LIVE_IMAGE_TEST=1 RUNECORE_ROOT="<Runecore repository path>" \
  python3 .github/skills/create-image/tests/test_create_image_skill.py
```
