from pathlib import Path
from typing import Any, Tuple, Optional
import os

from PIL.Image import Image
# from joblib import Parallel, delayed
from pdf2image import convert_from_path
from pydantic import BaseModel
import pyocr
import pyocr.builders

from cropper import Cropper


class FromImage(BaseModel):
    ocr: Any
    lang: str
    vertical: bool
    chapter: Optional[str]
    start_page: Optional[int] = None
    end_page: Optional[int] = None

    def read_image(self, source: Image) -> Tuple[Image, str]:
        options = {}
        if self.vertical:
            options['tesseract_layout'] = 5

        cropper = Cropper(image=source, ocr=self.ocr)
        cropper.remove_page_number(position='bottom')
        if self.chapter is not None:
            cropper.remove_chapter_title(position=self.chapter)

        source = cropper.image
        # source.save('/tmp/xmosh/cropped.png')

        builder = pyocr.builders.TextBuilder(**options)
        text = self.ocr.image_to_string(source, lang=self.lang, builder=builder)

        return source, text

    def read_pdf(self, pdf_file: Path, output: Path) -> None:
        print('Convert from PDF')

        images = convert_from_path(pdf_file)
        sp = (self.start_page or 1) - 1
        ep = (self.end_page or len(images))

        os.makedirs(output, exist_ok=True)

        tasks = [
            (index, image)
            for index, image in enumerate(images[sp:ep])
        ]

        def process(index: int, image: Image) -> None:
            page = index + 1
            print(f'Generate: page={page}')
            cropped, text = self.read_image(source=image)
            cropped.save(output / f'{page:04d}.png')
            with open(output / f'{page:04d}.txt', 'w') as f:
                print(text, file=f)

        for task in tasks:
            process(*task)
        # Parallel(n_jobs=-1)([delayed(process)(*n) for n in tasks])
