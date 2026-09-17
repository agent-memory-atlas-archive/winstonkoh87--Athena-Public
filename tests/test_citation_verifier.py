"""
tests.test_citation_verifier
============================

Unit tests for the Crossref citation verification engine.
"""

import unittest
from unittest.mock import MagicMock, patch

from athena.tools.citation_verifier import (
    _compute_token_similarity,
    extract_dois,
    normalize_doi,
    verify_doi,
)


class TestCitationVerifier(unittest.TestCase):
    def test_normalize_doi(self):
        self.assertEqual(normalize_doi("10.1038/s41586-020-2649-2"), "10.1038/s41586-020-2649-2")
        self.assertEqual(normalize_doi("https://doi.org/10.1038/s41586-020-2649-2"), "10.1038/s41586-020-2649-2")
        self.assertEqual(normalize_doi("http://dx.doi.org/10.1038/s41586-020-2649-2."), "10.1038/s41586-020-2649-2")
        self.assertEqual(normalize_doi("doi: 10.1038/s41586-020-2649-2"), "10.1038/s41586-020-2649-2")

    def test_extract_dois(self):
        text = """
        Here are references:
        1. See https://doi.org/10.1038/s41586-020-2649-2 for details.
        2. Another paper: doi:10.1145/3318464.3389700, and (10.1038/s41586-020-2649-2).
        """
        dois = extract_dois(text)
        self.assertEqual(len(dois), 2)
        self.assertIn("10.1038/s41586-020-2649-2", dois)
        self.assertIn("10.1145/3318464.3389700", dois)

    def test_compute_token_similarity(self):
        sim = _compute_token_similarity("Array programming with NumPy", "Array programming with NumPy")
        self.assertEqual(sim, 1.0)
        sim_partial = _compute_token_similarity("Array programming with NumPy", "NumPy: Array programming")
        self.assertGreater(sim_partial, 0.7)
        sim_zero = _compute_token_similarity("Array programming", "Deep Reinforcement Learning")
        self.assertEqual(sim_zero, 0.0)

    @patch("requests.get")
    def test_verify_doi_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "message": {
                "title": ["Attention Is All You Need"],
                "container-title": ["NeurIPS"],
                "volume": "30",
                "issue": "1",
                "page": "5998-6008",
                "published-print": {"date-parts": [[2017, 12]]},
                "author": [
                    {"given": "Ashish", "family": "Vaswani"},
                    {"given": "Noam", "family": "Shazeer"},
                ],
            }
        }
        mock_get.return_value = mock_resp

        res = verify_doi("10.5555/3295222.3295349", expected_title="Attention Is All You Need")
        self.assertTrue(res.valid)
        self.assertEqual(res.title, "Attention Is All You Need")
        self.assertEqual(res.journal, "NeurIPS")
        self.assertEqual(res.volume, "30")
        self.assertEqual(res.year, 2017)
        self.assertIn("Vaswani, Ashish", res.authors)
        self.assertTrue(res.title_match)
        self.assertIn("[PASS]", res.to_ascii_summary())

    @patch("requests.get")
    def test_verify_doi_404(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        res = verify_doi("10.1234/nonexistent")
        self.assertFalse(res.valid)
        self.assertIn("404", res.error)
        self.assertIn("[FAIL]", res.to_ascii_summary())

    def test_verify_doi_invalid_syntax(self):
        res = verify_doi("not-a-valid-doi")
        self.assertFalse(res.valid)
        self.assertIn("Invalid DOI syntax", res.error)


if __name__ == "__main__":
    unittest.main()
