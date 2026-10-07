import json
import os
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / ".github" / "skills" / "create-image" / "SKILL.md"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class CreateImageSkillContractTests(unittest.TestCase):
    def test_skill_documents_the_runecore_generation_and_validation_flow(self):
        self.assertTrue(SKILL.is_file(), f"Missing create-image skill: {SKILL}")
        skill = SKILL.read_text(encoding="utf-8")

        for requirement in (
            "name: create-image",
            "runecore_asset_pipeline generate",
            "runecore_asset_pipeline validate",
            "assets/generated/",
            "source.png",
            "OPENAI_API_KEY",
            "macOS Keychain",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, skill)

    def test_skill_protects_credentials_and_existing_assets(self):
        skill = SKILL.read_text(encoding="utf-8").lower()

        for requirement in (
            "never overwrite",
            "explicit confirmation",
            "never ask the user to paste a key",
            "may incur provider charges",
            "run_live_image_test=1",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, skill)


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_IMAGE_TEST") == "1",
    "set RUN_LIVE_IMAGE_TEST=1 to call the live image-generation model",
)
class LiveImageGenerationTests(unittest.TestCase):
    def test_runecore_pipeline_generates_and_validates_a_live_png(self):
        root_value = os.environ.get("RUNECORE_ROOT")
        self.assertTrue(root_value, "set RUNECORE_ROOT to the Runecore checkout")
        runecore = Path(root_value).expanduser().resolve()
        self.assertTrue(
            (runecore / "src" / "asset_pipeline" / "AssetPipeline.cpp").is_file(),
            "RUNECORE_ROOT must identify the Runecore repository",
        )

        pipeline_value = os.environ.get("RUNECORE_ASSET_PIPELINE")
        pipeline = (
            Path(pipeline_value).expanduser()
            if pipeline_value
            else runecore / "build" / "runecore_asset_pipeline"
        )
        if not pipeline.is_absolute():
            pipeline = runecore / pipeline
        self.assertTrue(
            pipeline.is_file(),
            "build the Runecore CLI with `cmake --build build --target runecore_asset_pipeline`",
        )

        generated_root = runecore / "assets" / "generated"
        self.assertTrue(generated_root.is_dir(), "Runecore generated asset directory is missing")

        with tempfile.TemporaryDirectory(
            prefix=".create-image-skill-live-test-",
            dir=generated_root,
        ) as temporary_category:
            category_path = Path(temporary_category)
            entity_path = category_path / "live_model_smoke_test"
            request_directory = entity_path / "sprite"
            request_directory.mkdir(parents=True)
            request_path = request_directory / "request.json"
            request = {
                "id": "create_image_live_test_sprite",
                "category": category_path.name,
                "label": "sprite",
                "prompt": (
                    "Create one original blue crystal icon centered on a transparent "
                    "background. Use a clear silhouette and no text."
                ),
                "style": "runecore_hybrid_v1",
                "presentation_tier": "pixel",
                "width": 128,
                "height": 128,
                "transparent_background": True,
                "animation_frames": 1,
            }
            request_path.write_text(
                json.dumps(request, indent=2) + "\n",
                encoding="utf-8",
            )
            relative_request = request_path.relative_to(runecore)

            generation = subprocess.run(
                [str(pipeline), "generate", str(relative_request)],
                cwd=runecore,
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )
            self.assertEqual(
                0,
                generation.returncode,
                "live image generation failed; provider output is suppressed to avoid credential leakage",
            )

            output_path = request_directory / "source.png"
            self.assertTrue(output_path.is_file(), "live generation did not create source.png")
            validation = subprocess.run(
                [str(pipeline), "validate", str(output_path.relative_to(runecore))],
                cwd=runecore,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(
                0,
                validation.returncode,
                "the Runecore CLI rejected the generated PNG",
            )

            image = output_path.read_bytes()
            self.assertTrue(image.startswith(PNG_SIGNATURE), "output is not a PNG")
            self.assertGreaterEqual(len(image), 24, "PNG is too short to contain an IHDR chunk")
            width, height = struct.unpack(">II", image[16:24])
            self.assertGreater(width, 0, "PNG width must be positive")
            self.assertGreater(height, 0, "PNG height must be positive")


if __name__ == "__main__":
    unittest.main()
