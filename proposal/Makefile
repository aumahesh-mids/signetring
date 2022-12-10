build: pdf

pdf:
	pdflatex proposal.tex
	bibtex proposal
	pdflatex proposal.tex
	pdflatex proposal.tex

clean:
	rm -f *.pdf
	rm -f *.out
	rm -f *.aux
	rm -f *.log
