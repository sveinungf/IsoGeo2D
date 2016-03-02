RHO ?= 0
PHI ?= 0
TEXSIZE ?= 256

VG_DIR = ./output/vg

pixels-direct:
	python vgpixels.py 0 1

pixels:
	python vgpixels.py 1 $(TEXSIZE)
	python vgpixels.py 2 $(TEXSIZE)
	python vgpixels.py 3 $(TEXSIZE)
	python vgpixels.py 4 $(TEXSIZE)

crop-graphs:
	pdfcrop $(VG_DIR)/graph_$(RHO),$(PHI)_legend.pdf
	pdfcrop $(VG_DIR)/graph_$(RHO),$(PHI)_max.pdf
	pdfcrop $(VG_DIR)/graph_$(RHO),$(PHI)_mean.pdf
	pdfcrop $(VG_DIR)/graph_$(RHO),$(PHI)_var.pdf

clean:
	find ./output/results -name "*.pkl" -type f -delete
	find $(VG_DIR) -name "*.pdf" -type f -delete
	find ./output/vgresults -name "*.pkl" -type f -delete

