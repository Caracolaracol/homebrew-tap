from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from update_formula import (  # noqa: E402
    TARGETS,
    archive_name,
    collect_checksums,
    release_url,
    render_formula,
)


class FormulaTests(unittest.TestCase):
    def setUp(self):
        self.tag = "v2026.10.1"
        self.release = {"tag_name": self.tag, "draft": False, "prerelease": False, "assets": []}
        for target in TARGETS:
            name = archive_name(self.tag, target)
            for asset in (name, f"{name}.sha256"):
                self.release["assets"].append({
                    "name": asset,
                    "browser_download_url": release_url(self.tag, asset),
                })

    @staticmethod
    def download(url):
        filename = url.rsplit("/", 1)[1].removesuffix(".sha256")
        return f"{'ab' * 32}  {filename}\n"

    def test_binary_only_formula_preserves_both_commands(self):
        tag, checksums = collect_checksums(self.release, self.download)
        formula = render_formula(tag, checksums)
        self.assertEqual(len(checksums), 4)
        self.assertEqual(formula.count('sha256 "'), 4)
        self.assertIn('bin.install "tuxedo"', formula)
        self.assertIn('bin.install_symlink "tuxedo" => "tuxedotask"', formula)
        self.assertIn('conflicts_with "tuxedo"', formula)
        self.assertNotIn('depends_on "rust"', formula)
        self.assertNotIn('cargo install', formula)
        self.assertEqual(formula, render_formula(tag, checksums))

    def test_refuses_partial_releases(self):
        self.release["assets"].pop()
        with self.assertRaises(ValueError):
            collect_checksums(self.release, self.download)

    def test_refuses_unexpected_asset_hosts(self):
        self.release["assets"][0]["browser_download_url"] = "https://example.invalid/binary"
        with self.assertRaises(ValueError):
            collect_checksums(self.release, self.download)

    def test_refuses_drafts_prereleases_and_unsafe_tags(self):
        for field in ("draft", "prerelease"):
            release = deepcopy(self.release)
            release[field] = True
            with self.assertRaises(ValueError):
                collect_checksums(release, self.download)
        for tag in ('v1.0.0"; abort', "v2026.10.1-beta", "main", ""):
            release = deepcopy(self.release)
            release["tag_name"] = tag
            with self.assertRaises(ValueError):
                collect_checksums(release, self.download)

    def test_refuses_invalid_checksum_or_wrong_filename(self):
        for payload in ("not-a-hash", f"{'ab' * 32}  wrong.tar.gz", f"{'xy' * 32}  wrong.tar.gz"):
            with self.assertRaises(ValueError):
                collect_checksums(self.release, lambda _: payload)

    def test_refuses_missing_or_injected_template_values(self):
        with self.assertRaises(ValueError):
            render_formula(self.tag, {})
        with self.assertRaises(ValueError):
            render_formula('v1.0.0"', {target: "ab" * 32 for target in TARGETS})


if __name__ == "__main__":
    unittest.main()
