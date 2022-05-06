from dataclasses import InitVar
from pathlib import Path
from typing import Any, Tuple, Optional
import os
import re

from PIL import Image, ImageOps
from pydantic import BaseModel
import click
import pyocr
import pyocr.builders

from cropper import Cropper
from kindle import Kindle

# https://gitlab.gnome.org/World/OpenPaperwork/pyocr
# https://child-programmer.com/ai/ocr/python/japanese-vertical/
# https://motojapan.hateblo.jp/entry/2018/03/12/094636

local_tessdata = Path(os.path.expanduser('~/.local/share/tessdata'))
if local_tessdata.is_dir():
    os.environ['TESSDATA_PREFIX'] = str(local_tessdata)


def get_ocr_tool() -> Any:
    ocr_tools = pyocr.get_available_tools()
    assert len(ocr_tools) == 1
    return ocr_tools[0]


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument('destination', type=click.Path(exists=False, dir_okay=True))
@click.option('--minimum-pages', type=int, default=10)
def kindle(destination: Path, minimum_pages: int) -> None:
    app = Kindle.prepare(minimum_pages=minimum_pages, ocr=get_ocr_tool())
    app.start(Path(destination))


@main.command()
@click.argument('image_file', type=click.Path(exists=False, dir_okay=True))
@click.option('--lang', type=str, default='eng')
@click.option('--vertical', type=bool, default=False, is_flag=True)
@click.option('--chapter', type=str, default=None)
def from_file(image_file: Path, lang: str, vertical: bool, chapter: Optional[str] = None) -> None:
    ocr = get_ocr_tool()
    source = Image.open(image_file)

    options = {}
    if vertical:
        options['tesseract_layout'] = 5

    cropper = Cropper(image=source, ocr=ocr)
    cropper.remove_page_number(position='bottom')
    if chapter is not None:
        cropper.remove_chapter_title(position=chapter)

    source = cropper.image
    # source.save('/tmp/xmosh/cropped.png')

    builder = pyocr.builders.TextBuilder(**options)
    text = ocr.image_to_string(source, lang=lang, builder=builder)
    print(text)


@main.command()
def languages() -> None:
    ocr = get_ocr_tool()
    ls = ocr.get_available_languages()
    print(ls)


if __name__ == '__main__':
    main()
