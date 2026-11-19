"""Copy assets/entry.png to the output directory as entry.png.

Standard library only. No randomness, no timestamps: the output is a
byte-for-byte copy of the source image, so repeated runs are identical.
"""

import os
import shutil
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    source = repo_root / "assets" / "entry.png"
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = repo_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out_dir / "entry.png")


if __name__ == "__main__":
    main()
