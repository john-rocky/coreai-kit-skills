import copy
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/integrate-coreai/scripts/resolve_model.py"
spec = importlib.util.spec_from_file_location("resolve_model", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Small fixture from CoreAIKit 0.4.1's qwen3-0.6b entry, not a second model catalog.
MODEL = {
    "id": "qwen3-0.6b", "name": "Qwen3 0.6B", "kind": "chat",
    "repo": "mlboydaisuke/qwen3-0.6b-CoreAI-official",
    "revision": "943eb6a4f967de53d7e1458d75deac0b68ac3d85",
    "variants": {"macos": {"path": "macos", "sizeMB": 352},
                 "ios": {"path": "ios", "sizeMB": 456}},
}


class ModelResolutionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {"version": 1, "models": [copy.deepcopy(MODEL)]}

    def resolve(self, **kwargs):
        return module.resolve(self.catalog, release="0.4.1", **kwargs)

    def test_platforms_resolve_separate_paths_and_sizes(self):
        mac = self.resolve(platform="macos", model_id="qwen3-0.6b")["models"][0]
        ios = self.resolve(platform="ios", model_id="qwen3-0.6b")["models"][0]
        self.assertEqual(mac["variant"], {"path": "macos", "sizeMB": 352})
        self.assertEqual(ios["variant"], {"path": "ios", "sizeMB": 456})
        self.assertTrue(mac["artifact_url"].endswith(MODEL["revision"] + "/macos"))
        self.assertTrue(ios["artifact_url"].endswith(MODEL["revision"] + "/ios"))

    def test_external_catalog_alias_is_not_silently_accepted(self):
        with self.assertRaisesRegex(ValueError, "Unknown CoreAIKit ID"):
            self.resolve(platform="macos", model_id="official-qwen3-0-6b")

    def test_missing_ios_variant_cannot_fall_back_to_mac(self):
        del self.catalog["models"][0]["variants"]["ios"]
        with self.assertRaisesRegex(ValueError, "no ios variant"):
            self.resolve(platform="ios", model_id="qwen3-0.6b")
        self.assertEqual(self.resolve(platform="ios", kind="chat")["models"], [])

    def test_mutable_model_revision_is_rejected(self):
        self.catalog["models"][0]["revision"] = "main"
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.resolve(platform="macos")

    def test_task_and_id_must_agree(self):
        second = copy.deepcopy(MODEL)
        second.update(id="test-tts", kind="tts")
        self.catalog["models"].append(second)
        self.assertEqual([m["id"] for m in self.resolve(platform="macos", kind="chat")["models"]], ["qwen3-0.6b"])
        with self.assertRaisesRegex(ValueError, "does not have kind"):
            self.resolve(platform="macos", model_id="qwen3-0.6b", kind="tts")

    def test_duplicate_identity_is_rejected(self):
        self.catalog["models"].append(copy.deepcopy(MODEL))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.resolve(platform="macos")

    def test_catalog_path_cannot_escape_repository(self):
        self.catalog["models"][0]["variants"]["macos"]["path"] = "../../another-repo"
        with self.assertRaisesRegex(ValueError, "invalid variant path"):
            self.resolve(platform="macos")

    def test_bundle_at_hugging_face_repository_root_is_valid(self):
        self.catalog["models"][0]["variants"]["macos"]["path"] = ""
        model = self.resolve(platform="macos")["models"][0]
        self.assertTrue(model["artifact_url"].endswith(MODEL["revision"] + "/"))


if __name__ == "__main__":
    unittest.main()
