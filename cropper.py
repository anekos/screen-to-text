from dataclasses import dataclass
from typing import Any, List
from math import ceil, floor
import re

import pyocr
import pyocr.builders


@dataclass
class Cropper:
    ocr: Any
    image: Any

    def _crop(self, edges: List[float], position: str) -> None:
        if len(edges) == 0:
            return

        edges.sort(reverse=position == 'bottom')
        edge = edges[0]

        if position == 'top':
            # 章題が含まれていると、ちょっとはみ出ることがあるので、少し余計に切りとる
            edge += edge * 0.01
            h = floor(self.image.height * edge)
            cropped = self.image.crop((0, h, self.image.width, self.image.height))
        else:
            edge -= edge * 0.01
            h = ceil(self.image.height * edge)
            cropped = self.image.crop((0, 0, self.image.width, h))
        self.image = cropped

    def remove_page_number(self, position: str) -> None:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=3)

        lbs = self.ocr.image_to_string(image=self.image, lang='eng', builder=builder)
        edges = []

        for lb in lbs:
            ((left, top), (right, bottom)) = lb.position
            rel_top = top / self.image.height
            rel_bottom = bottom / self.image.height
            if re.match('^[0-9IOol]+', lb.content) is None:
                continue
            if position == 'top' and rel_bottom < 0.1:
                edges.append(rel_bottom)
                # print(f'{rel_bottom} = {lb.content}')
            elif position == 'bottom' and 0.9 < rel_top:
                edges.append(rel_top)
                # print(f'{rel_top} = {lb.content}')

        self._crop(edges, position)

    def remove_chapter_title(self, position: str) -> None:
        builder = pyocr.builders.LineBoxBuilder(tesseract_layout=3)

        lbs = self.ocr.image_to_string(image=self.image, lang='jpn', builder=builder)
        edges = []

        for lb in lbs:
            ((left, top), (right, bottom)) = lb.position
            rel_top = top / self.image.height
            rel_bottom = bottom / self.image.height
            if position == 'top' and rel_bottom < 0.3:
                edges.append(rel_bottom)
                # print(f'{rel_bottom} = {lb.content}')
            elif position == 'bottom' and 0.9 < rel_top:
                edges.append(rel_bottom)
                # print(f'{rel_top} = {lb.content}')

        self._crop(edges, position)

# builder = pyocr.builders.LineBoxBuilder(**options)
# lbs = ocr.image_to_string(source, lang=lang, builder=builder)
# for lb in lbs:
#     print(lb.position)
#     print('  ' + lb.content)
