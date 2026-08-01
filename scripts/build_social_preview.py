"""Render the GPAP² social preview from a simple data-led visual system."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "gpap2-social-preview.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    windows = Path("C:/Windows/Fonts")
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = windows / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def main() -> None:
    image = Image.new("RGB", (1280, 640), "#0f2638")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, 640), fill="#3caea3")
    draw.text((72, 58), "GPAP²", font=font(74, True), fill="white")
    draw.text(
        (72, 160),
        "From digital activity to access pressure profiles",
        font=font(39, True),
        fill="#e8f2f5",
    )
    draw.text(
        (74, 220),
        "Recorded activity | Machine learning | Evidence readiness",
        font=font(25),
        fill="#9fd8d3",
    )

    cards = [
        ("6,067", "English practices", "#20639b"),
        ("14", "national features", "#3caea3"),
        ("3", "activity profiles", "#ed9f44"),
    ]
    for index, (value, label, colour) in enumerate(cards):
        left = 72 + index * 310
        draw.rounded_rectangle((left, 330, left + 270, 505), radius=24, fill=colour)
        draw.text((left + 25, 354), value, font=font(55, True), fill="white")
        draw.text((left + 25, 435), label, font=font(22), fill="white")

    draw.text(
        (72, 566),
        "England | April 2025 to March 2026 | Reproducible analytical companion",
        font=font(22),
        fill="#c9dbe3",
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
