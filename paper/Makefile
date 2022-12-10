build: pdf

pdf:
	rm -f *.bbl
	pdflatex main.tex
	bibtex main
	pdflatex main.tex
	pdflatex main.tex
	rm -f *.cpt
	rm -f *.out
	rm -f *.aux
	rm -f *.log
	rm -f *.bbl

clean:
	rm -f *.pdf
	rm -f *.out
	rm -f *.aux
	rm -f *.log
	rm -f *.bbl
