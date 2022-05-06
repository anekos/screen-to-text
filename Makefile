
DATA_DIR = ~/.local/share/tessdata/


pacman:
	sudo pacman -S community/tesseract community/tesseract-data-eng community/tesseract-data-jpn community/tesseract-data-jpn_vert


traindata:
	mkdir -p $(DATA_DIR)
	wget -O $(DATA_DIR)/jpn_vert.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn_vert.traineddata
	wget -O $(DATA_DIR)/jpn.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata
	wget -O $(DATA_DIR)/eng.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata
	wget -O $(DATA_DIR)/osd.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/osd.traineddata
