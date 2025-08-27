from pathlib import Path


def _style_path(name: str) -> Path:
    """Return the absolute Path to a style file inside the package."""
    return Path(__file__).parent.joinpath("styles", name)

available_styles: list[str] = [
    style.stem
    for style in Path(__file__).parent.joinpath("styles").iterdir()
    if style.suffix == ".mplstyle"
]


charcoal: str = _style_path("charcoal.mplstyle").as_posix()
forestdark: str = _style_path("forestdark.mplstyle").as_posix()
forestdark2: str = _style_path("forestdark2.mplstyle").as_posix()
forestlight: str = _style_path("forestlight.mplstyle").as_posix()
ivorygrid: str = _style_path("ivorygrid.mplstyle").as_posix()
sealight: str = _style_path("sealight.mplstyle").as_posix()
coastalarvest: str = _style_path("coastalarvest.mplstyle").as_posix()