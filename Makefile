TEXSIZE ?= 256

pixels-direct:
	python vgpixels.py 0 1

pixels:
	python vgpixels.py 1 $(TEXSIZE)
	python vgpixels.py 2 $(TEXSIZE)
	python vgpixels.py 3 $(TEXSIZE)
	python vgpixels.py 4 $(TEXSIZE)

clean:
	find ./output/results -name "*.pkl" -type f -delete
	find ./output/vg -name "*.pdf" -type f -delete
	find ./output/vgresults -name "*.pkl" -type f -delete

