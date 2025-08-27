import matplotlib.pyplot as plt
import pytest

import matplotlib as mpl
import numpy as np
from matplotlib import colors


# --- WCAG luminance and contrast functions ---
def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    r, g, b = srgb_to_linear(np.array(rgb))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1, c2):
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    l_light, l_dark = max(l1, l2), min(l1, l2)
    return (l_light + 0.05) / (l_dark + 0.05)


# --- Single function to test one style ---
def check_style_legibility(style_name, style_obj, threshold=4.5):
    """Check that text, axis labels, and ticks meet WCAG AA contrast."""
    with plt.style.context(style_obj):
        failures = []
        style_dict = mpl.rcParams
        axes_facecolor = colors.to_rgb(style_dict.get("axes.facecolor", "white"))
        figure_facecolor = colors.to_rgb(style_dict.get("figure.facecolor", "white"))

        for element_name, rc_key in [
            ("Text", "text.color"),
        ]:
            foreground_color = colors.to_rgb(style_dict.get(rc_key, "black"))

            # Convert to 0–255 for WCAG math
            bg_rgb_255 = tuple(int(c * 255) for c in axes_facecolor)
            fg_rgb_255 = tuple(int(c * 255) for c in foreground_color)

            cr = contrast_ratio(bg_rgb_255, fg_rgb_255)
            if cr < threshold:
                failures.append(f"{element_name} contrast {cr:.2f} below {threshold}")

        for element_name, rc_key in [
            ("Axis labels", "axes.labelcolor"),
            ("Ticks", "xtick.color"),
            ("Axes Title", "axes.titlecolor"),
        ]:
            foreground_color = colors.to_rgb(style_dict.get(rc_key, "black"))

            # Convert to 0–255 for WCAG math
            bg_rgb_255 = tuple(int(c * 255) for c in figure_facecolor)
            fg_rgb_255 = tuple(int(c * 255) for c in foreground_color)

            cr = contrast_ratio(bg_rgb_255, fg_rgb_255)
            if cr < threshold:
                failures.append(f"{element_name} contrast {cr:.2f} below {threshold}")

        if failures:
            fail_msg = f"Style '{style_name}' failed contrast checks:\n" + "\n".join(
                failures
            )
            pytest.fail(fail_msg)


# --- Pytest tests for each style ---
def test_charcoal_legibility():
    from cool_styles import charcoal

    check_style_legibility("charcoal", charcoal)


def test_forestdark_legibility():
    from cool_styles import forestdark

    check_style_legibility("forestdark", forestdark)


def test_forestlight_legibility():
    from cool_styles import forestlight

    check_style_legibility("forestlight", forestlight)


def test_ivorygrid_legibility():
    from cool_styles import ivorygrid

    check_style_legibility("ivorygrid", ivorygrid)


def test_sealight_legibility():
    from cool_styles import sealight

    check_style_legibility("sealight", sealight)


def test_coastalarvest_legibility():
    from cool_styles import coastalarvest

    check_style_legibility("coastalarvest", coastalarvest)
