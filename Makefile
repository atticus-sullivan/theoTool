.PHONY: clean

tikzPy.pdf: tikzPy.tex
	latexmk -xelatex tikzPy.tex

clean:
	$(RM) *.aux *.fls *.fdb_latexmk *.log *.out *.toc *.xdv
