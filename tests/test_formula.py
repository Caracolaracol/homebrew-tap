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

    def test_semver_keeps_the_epoch_after_calver(self):
        checksums = {target: "ab" * 32 for target in TARGETS}
        for tag in ("v1.0.0", "v1.0.1", "v1.1.0", "v2.0.0"):
            formula = render_formula(tag, checksums)
            self.assertIn('version_scheme 1', formula)
            self.assertIn('assert_equal 1, version_scheme', formula)
            self.assertIn(f'version "{tag[1:]}"', formula)
        for tag in ("v2026.10.3", "v2026.10.4"):
            formula = render_formula(tag, checksums)
            self.assertNotIn('  version_scheme 1', formula)
            self.assertIn('assert_equal 0, version_scheme', formula)

    def test_collects_semver_release_assets(self):
        tag = "v1.0.0"
        release = {"tag_name": tag, "draft": False, "prerelease": False, "assets": []}
        for target in TARGETS:
            filename = archive_name(tag, target)
            for name in (filename, f"{filename}.sha256"):
                release["assets"].append({
                    "name": name, "browser_download_url": release_url(tag, name),
                })
        actual, checksums = collect_checksums(release, self.download)
        self.assertEqual(actual, tag)
        self.assertIn('version_scheme 1', render_formula(actual, checksums))

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
