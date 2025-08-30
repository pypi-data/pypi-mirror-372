import re
from pathlib import Path
from typing import Optional, Set, Tuple

import pytest

CONFIG_PATTERN: re.Pattern[str] = re.compile(
    pattern=r"^\s*([^:\s]+(?:\.[^:\s]+)*)\s*:\s*([^#\n\r]*)(?:\s*#.*)?\s*$"
)

REQUIRED_RCPARAMS = frozenset([
    "figure.figsize",
    "figure.dpi", 
    "figure.constrained_layout.use",
    "font.size",
    "axes.axisbelow",
    "axes.spines.top",
    "axes.spines.right",
    "axes.prop_cycle",
    "axes.grid",
    "grid.linestyle",
    "grid.linewidth",
    "grid.alpha",
    "legend.fancybox",
    "image.cmap",
    "hist.bins",
    "savefig.format",
    "savefig.transparent",
    "legend.columnspacing",
    "savefig.dpi",
    "legend.frameon",
    "lines.linewidth",
    "axes.grid.which",
    "legend.framealpha",
])


def parse_rcparam_line(style_text: str) -> Optional[Tuple[str, str]]:
    """Parse a line from a matplotlib style file.
    
    Args:
        style_text: A single line from a style file
        
    Returns
    -------
        Tuple of (key, value) if line contains a valid rcParam, None otherwise
    """
    stripped = style_text.strip()
    if not stripped or stripped.startswith("#"):
        return None
        
    match = CONFIG_PATTERN.match(stripped)
    if match:
        key = match.group(1).strip()
        value = match.group(2).strip()
        return key, value
    return None


def get_defined_rcparams(stylesheet_path: Path) -> Set[str]:
    """Extract all rcParam keys defined in a stylesheet.
    
    Args:
        stylesheet_path: Path to the matplotlib style file
        
    Returns
    -------
        Set of rcParam keys found in the file
        
    Raises
    ------
        FileNotFoundError: If stylesheet doesn't exist
        PermissionError: If stylesheet can't be read
    """
    defined_params = set()
    
    try:
        with stylesheet_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    parsed = parse_rcparam_line(line)
                    if parsed:
                        defined_params.add(parsed[0])
                except Exception as e:
                    # Log parsing error but continue processing
                    print(f"Warning: Error parsing line {line_num} in {stylesheet_path}: {e}")
                    
    except (FileNotFoundError, PermissionError) as e:
        raise type(e)(f"Cannot read stylesheet {stylesheet_path}: {e}") from e
        
    return defined_params


def assert_style_completeness(style_name: str, stylesheet_path: str) -> None:
    """Assert that a style file defines all required rcParams.
    
    Args:
        style_name: Name of the style for error messages
        stylesheet_path: Path to the stylesheet file (as string or Path)
    """
    path = Path(stylesheet_path)
    
    if not path.exists():
        pytest.fail(f"Stylesheet {path} does not exist")
    
    defined_params = get_defined_rcparams(path)
    missing_params = REQUIRED_RCPARAMS - defined_params
    
    if missing_params:
        sorted_missing = sorted(missing_params)
        pytest.fail(f"Style '{style_name}' missing required rcParams: {', '.join(sorted_missing)}")


# Parametrized test approach - more maintainable
@pytest.mark.parametrize("style_name,import_path", [
    ("charcoal", "cool_styles.charcoal"),
    ("coastalarvest", "cool_styles.coastalarvest"), 
    ("forestdark", "cool_styles.forestdark"),
    ("ivorygrid", "cool_styles.ivorygrid"),
    ("sealight", "cool_styles.sealight"),
    ("forestlight", "cool_styles.forestlight"),
])
def test_style_completeness(style_name: str, import_path: str):
    """Test that each style defines all required rcParams."""
    try:
        # Dynamic import to get the stylesheet path
        module_parts = import_path.split(".")
        module_name = ".".join(module_parts[:-1])
        attr_name = module_parts[-1]
        
        module = __import__(module_name, fromlist=[attr_name])
        stylesheet_path = getattr(module, attr_name)
        
        assert_style_completeness(style_name, stylesheet_path)
        
    except ImportError as e:
        pytest.skip(f"Cannot import {import_path}: {e}")
    except AttributeError as e:
        pytest.fail(f"Module {module_name} has no attribute {attr_name}: {e}")


# Alternative: Individual test functions (if parametrization isn't preferred)
def test_charcoal_completeness():
    """Test that charcoal style defines all required rcParams."""
    try:
        from cool_styles import charcoal
        assert_style_completeness("charcoal", charcoal)
    except ImportError:
        pytest.skip("cool_styles.charcoal not available")


def test_coastalarvest_completeness():
    """Test that coastalarvest style defines all required rcParams.""" 
    try:
        from cool_styles import coastalarvest
        assert_style_completeness("coastalarvest", coastalarvest)
    except ImportError:
        pytest.skip("cool_styles.coastalarvest not available")


def test_forestdark_completeness():
    """Test that forestdark style defines all required rcParams."""
    try:
        from cool_styles import forestdark
        assert_style_completeness("forestdark", forestdark)
    except ImportError:
        pytest.skip("cool_styles.forestdark not available")


def test_ivorygrid_completeness():
    """Test that ivorygrid style defines all required rcParams."""
    try:
        from cool_styles import ivorygrid
        assert_style_completeness("ivorygrid", ivorygrid)
    except ImportError:
        pytest.skip("cool_styles.ivorygrid not available")


def test_sealight_completeness():
    """Test that sealight style defines all required rcParams."""
    try:
        from cool_styles import sealight
        assert_style_completeness("sealight", sealight)
    except ImportError:
        pytest.skip("cool_styles.sealight not available")


def test_forestlight_completeness():
    """Test that forestlight style defines all required rcParams."""
    try:
        from cool_styles import forestlight
        assert_style_completeness("forestlight", forestlight)
    except ImportError:
        pytest.skip("cool_styles.forestlight not available")


def test_goldenpeachy_completeness():
    """Test that goldenpeachy style defines all required rcParams."""
    try:
        from cool_styles import goldenpeachy

        assert_style_completeness("goldenpeachy", goldenpeachy)
    except ImportError:
        pytest.skip("cool_styles.goldenpeachy not available")