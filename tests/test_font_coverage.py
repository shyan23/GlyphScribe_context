"""
Test suite for verifying font coverage in generated images.

This module tests whether all available fonts are being used
during batch image generation by analyzing JSON metadata files.
"""
import json
from pathlib import Path
from collections import Counter
from typing import List, Set, Dict
import pytest


class FontAnalyzer:
    """Analyzer for font usage in generated images."""

    def __init__(self, fonts_dir: str):
        """
        Initialize the FontAnalyzer.

        Args:
            fonts_dir: Path to directory containing font files
        """
        self.fonts_dir = Path(fonts_dir)

    def get_all_fonts(self) -> Set[str]:
        """
        Get all font filenames from the fonts directory.

        Returns:
            Set of font filenames
        """
        font_paths = []
        for ext in ['*.ttf', '*.otf']:
            font_paths.extend(self.fonts_dir.rglob(ext))
        return {path.name for path in font_paths}

    def get_used_fonts(self, json_dir: str) -> List[str]:
        """
        Extract used fonts from JSON metadata files.

        Args:
            json_dir: Path to directory containing JSON metadata

        Returns:
            List of font filenames used in generation
        """
        json_path = Path(json_dir)
        used_fonts = []

        for json_file in json_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    font_used = data.get('font_path_used', '')
                    if font_used:
                        used_fonts.append(Path(font_used).name)
            except (json.JSONDecodeError, IOError) as e:
                pytest.fail(f"Failed to read {json_file}: {e}")

        return used_fonts

    def calculate_coverage(self, all_fonts: Set[str], used_fonts: List[str]) -> Dict:
        """
        Calculate font coverage statistics.

        Args:
            all_fonts: Set of all available fonts
            used_fonts: List of fonts used in generation

        Returns:
            Dictionary containing coverage statistics
        """
        used_font_set = set(used_fonts)
        unused_fonts = all_fonts - used_font_set
        coverage_percent = (len(used_font_set) / len(all_fonts) * 100) if all_fonts else 0

        font_counts = Counter(used_fonts)

        return {
            'total_fonts': len(all_fonts),
            'used_fonts': len(used_font_set),
            'unused_fonts': unused_fonts,
            'coverage_percent': coverage_percent,
            'font_counts': font_counts,
            'all_fonts': all_fonts,
            'used_font_set': used_font_set
        }


# Fixtures
@pytest.fixture(scope="session")
def fonts_dir():
    """Fixture providing the fonts directory path."""
    return "bangla_fonts"


@pytest.fixture(scope="session")
def json_dir():
    """Fixture providing the JSON output directory path."""
    return "out/batch/json"


@pytest.fixture(scope="session")
def font_analyzer(fonts_dir):
    """Fixture providing a FontAnalyzer instance."""
    return FontAnalyzer(fonts_dir)


@pytest.fixture(scope="session")
def coverage_stats(font_analyzer, json_dir):
    """Fixture providing font coverage statistics."""
    all_fonts = font_analyzer.get_all_fonts()
    used_fonts = font_analyzer.get_used_fonts(json_dir)
    return font_analyzer.calculate_coverage(all_fonts, used_fonts)


# Test Cases
class TestFontDiscovery:
    """Tests for font discovery functionality."""

    def test_fonts_directory_exists(self, fonts_dir):
        """Test that the fonts directory exists."""
        assert Path(fonts_dir).exists(), f"Fonts directory not found: {fonts_dir}"

    def test_fonts_found(self, font_analyzer):
        """Test that fonts are discovered in the fonts directory."""
        fonts = font_analyzer.get_all_fonts()
        assert len(fonts) > 0, "No fonts found in fonts directory"

    def test_font_extensions(self, font_analyzer):
        """Test that discovered fonts have valid extensions."""
        fonts = font_analyzer.get_all_fonts()
        for font in fonts:
            assert font.endswith(('.ttf', '.otf')), f"Invalid font extension: {font}"


class TestJSONMetadata:
    """Tests for JSON metadata files."""

    def test_json_directory_exists(self, json_dir):
        """Test that the JSON output directory exists."""
        assert Path(json_dir).exists(), f"JSON directory not found: {json_dir}"

    def test_json_files_exist(self, json_dir):
        """Test that JSON files are present in the output directory."""
        json_files = list(Path(json_dir).glob("*.json"))
        assert len(json_files) > 0, f"No JSON files found in {json_dir}"

    def test_json_structure(self, json_dir):
        """Test that JSON files have the expected structure."""
        json_files = list(Path(json_dir).glob("*.json"))
        assert len(json_files) > 0, "No JSON files to test"

        # Test first JSON file
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_fields = ['font_path_used', 'text', 'font_size', 'output_path']
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing in JSON"


class TestFontCoverage:
    """Tests for font coverage in generated images."""

    def test_all_fonts_used(self, coverage_stats):
        """Test that all available fonts have been used at least once."""
        unused = coverage_stats['unused_fonts']
        assert len(unused) == 0, (
            f"{len(unused)} fonts were not used: {sorted(unused)}\n"
            f"Generate at least {coverage_stats['total_fonts']} images "
            f"to ensure all fonts are covered."
        )

    def test_minimum_coverage(self, coverage_stats):
        """Test that at least 80% of fonts are used."""
        coverage = coverage_stats['coverage_percent']
        assert coverage >= 80.0, (
            f"Font coverage is {coverage:.1f}%, expected at least 80%"
        )

    def test_font_distribution(self, coverage_stats):
        """Test that fonts are used in a reasonably balanced way."""
        font_counts = coverage_stats['font_counts']

        if len(font_counts) == 0:
            pytest.fail("No fonts were used in generation")

        min_usage = min(font_counts.values())
        max_usage = max(font_counts.values())
        avg_usage = sum(font_counts.values()) / len(font_counts)

        # Check that distribution isn't too skewed
        # Max usage should not be more than 3x the average
        assert max_usage <= avg_usage * 3, (
            f"Font distribution is skewed. "
            f"Min: {min_usage}, Max: {max_usage}, Avg: {avg_usage:.1f}"
        )


class TestGenerationQuality:
    """Tests for generation quality metrics."""

    def test_sufficient_samples(self, coverage_stats):
        """Test that enough images were generated to cover all fonts."""
        total_fonts = coverage_stats['total_fonts']
        font_counts = coverage_stats['font_counts']
        total_images = sum(font_counts.values()) if font_counts else 0

        assert total_images >= total_fonts, (
            f"Generated {total_images} images, but need at least "
            f"{total_fonts} to potentially cover all fonts"
        )

    def test_no_duplicate_processing(self, json_dir):
        """Test that there are no duplicate output paths in JSON files."""
        json_files = list(Path(json_dir).glob("*.json"))
        output_paths = []

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                output_paths.append(data.get('output_path', ''))

        unique_paths = set(output_paths)
        assert len(output_paths) == len(unique_paths), (
            f"Found {len(output_paths) - len(unique_paths)} duplicate output paths"
        )


# Reporting function for verbose output
def print_coverage_report(coverage_stats):
    """
    Print detailed coverage report.

    Args:
        coverage_stats: Coverage statistics dictionary
    """
    print("\n" + "="*60)
    print("Font Coverage Report")
    print("="*60)
    print(f"Total fonts available:     {coverage_stats['total_fonts']}")
    print(f"Total fonts used:          {coverage_stats['used_fonts']}")
    print(f"Coverage:                  {coverage_stats['coverage_percent']:.1f}%")

    if coverage_stats['unused_fonts']:
        print(f"\nUnused fonts ({len(coverage_stats['unused_fonts'])}):")
        for font in sorted(coverage_stats['unused_fonts']):
            print(f"  - {font}")

    font_counts = coverage_stats['font_counts']
    if font_counts:
        print(f"\nUsage statistics:")
        print(f"  Min: {min(font_counts.values())} times")
        print(f"  Max: {max(font_counts.values())} times")
        print(f"  Avg: {sum(font_counts.values()) / len(font_counts):.1f} times")

    print("="*60)


@pytest.fixture(scope="session", autouse=True)
def print_report(coverage_stats):
    """Automatically print coverage report after tests."""
    yield
    print_coverage_report(coverage_stats)
