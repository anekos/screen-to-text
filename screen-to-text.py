from dataclasses import InitVar
from pathlib import Path
from random import random
from typing import Any, Tuple
import os
import re
import time

from PIL import Image, ImageOps
from pydantic import BaseModel
import click
import pyautogui as pag
import pyocr
import pyocr.builders


def countdown(action_name: str, n: int = 6) -> None:
    print(f'Countdown to {action_name}')
    for i in range(n, 0, -1):
        print(i)
        time.sleep(1.0)
    print('0!')


def get_ocr_tool() -> Any:
    ocr_tools = pyocr.get_available_tools()
    assert len(ocr_tools) == 1
    return ocr_tools[0]


def is_text_page(image: Any) -> bool:
    mono = image.convert('L')
    hist = mono.histogram()
    total = 0.0
    for h in hist:
        total += h
    return 0.8 < (hist[-1] / total)


def cleanup(s: str) -> str:
    return re.sub(r'''\W+''', ' ', s)


def crop_image(image: Any) -> Any:
    inverted_image = ImageOps.invert(image)
    return image.crop(inverted_image.getbbox())


class App(BaseModel):
    next_button: Tuple[int, int]
    region: Tuple[int, int, int, int]
    ocr: Any
    builder: Any
    interval: int
    minimum_pages: int

    def start(self, destination: Path) -> None:
        os.makedirs(destination, exist_ok=True)
        last_text = ''
        n = 1
        while True:
            screenshot = pag.screenshot(region=self.region)
            text = self.ocr.image_to_string(screenshot, lang='eng', builder=self.builder)
            if last_text == text and self.minimum_pages < n:
                break

            with open(destination / f'{n:04d}.txt', 'w') as f:
                if is_text_page(screenshot):
                    print(text, file=f)
                else:
                    print('', file=f)

            screenshot.save(destination / f'{n:04d}.png')
            crop_image(screenshot).save(destination / f'{n:04d}.cropped.png')
            last_text = text
            print(f'  → {cleanup(text)[0:40]}')
            pag.click(*self.next_button, 1)
            time.sleep(self.interval + random() * 1.5)
            n += 1


@click.command()
@click.argument('destination', type=click.Path(exists=False, dir_okay=True))
@click.option('--minimum-pages', type=int, default=10)
def main(destination: Path, minimum_pages: int) -> None:
    countdown('Get the top left of region')
    left, top = pag.position()

    countdown('Get the bottom right of region')
    right, bottom = pag.position()

    countdown('Get the position of the button to go next page')
    next_button = pag.position()

    input('Press enter to start')

    countdown('Start')

    app = App(
        ocr=get_ocr_tool(),
        builder=pyocr.builders.TextBuilder(),
        next_button=next_button,
        region=(left, top, right - left, bottom - top),
        interval=1,
        minimum_pages=minimum_pages
    )
    app.start(Path(destination))


if __name__ == '__main__':
    main()
