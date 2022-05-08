from pathlib import Path
from typing import Any, Tuple, Optional

from PIL.Image import Image
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
        source.save('/tmp/xmosh/cropped.png')

        builder = pyocr.builders.TextBuilder(**options)
        text = self.ocr.image_to_string(source, lang=self.lang, builder=builder)

        return source, text

    def read_pdf(self, pdf_file: Path) -> None:
        images = convert_from_path(pdf_file)
        sp = (self.start_page or 1) - 1
        ep = (self.end_page or len(images))
        for image in images[sp:ep]:
            cropped, text = self.read_image(source=image)
            print(text)
