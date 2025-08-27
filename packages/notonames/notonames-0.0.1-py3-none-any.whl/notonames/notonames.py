"""Fixes names of files.

    blah.svg.svg => blah.svg
    blah.ai.svg => blah.svg
    blah.svg.png => blah.png
    blah.ai.png => blah.png

Converts u191d_u1f3b.svg or u191d-u1f3b.svg => emoji_u191d_1f3b.svg
Removes fe0f segments

Returns non-zero if any file was renamed.
"""

from absl import app
from pathlib import Path


_SUFFIX_FIXES = (
    (".svg.svg", ".svg"),
    (".ai.svg", ".svg"),
    (".svg.png", ".png"),
    (".ai.png", ".png"),
    (".png.png", ".png"),
)


def rename(current: Path) -> bool:
    parts = re.split("[-_]", file.stem)
    parts[0] = parts[0].removeprefix("emoji_u")
    parts[0] = parts[0].removeprefix("emoji")
    if not parts[0]:
        parts.pop(0)
    parts = [p.removeprefix("u") for p in parts]
    parts = [p for p in parts if p.lower() != "fe0f"]
    new_file = file.parent / ("emoji_u" + "_".join(p for p in parts if p) + file.suffix)
    for (bad_suffix, good_suffix) in _SUFFIX_FIXES:
        if new_file.name.endswith(bad_suffix):
            new_file = new_file.parent / new_file.name.replace(bad_suffix, "." + good_suffix)
    if file != new_file:
        print(file, "=>", new_file)
        file.rename(new_file)
    return file != new_file



def _run(argv):
    renamed = 0
    for dir_name in argv[1:]:
        for file in Path(dir_name).rglob("*"):
            if not file.is_file():
                continue
            if rename(file):
                renamed += 1

    if renamed > 0:
        return 1
    return 0


def main(argv=None):
    # We don't seem to be __main__ when run as cli tool installed by setuptools
    app.run(_run, argv=argv)


if __name__ == "__main__":
    main()