#!/bin/sh
# Generate config if not present and generate documentation
cd /doxy/docs
if [ ! -f "Doxyfile" ]; then doxygen -g; fi
doxygen Doxyfile

# Generate pdf from tex
cd /doxy/docs/latex

# Run pdflatex to compile the TeX files into a PDF
pdflatex refman.tex

# Run makeindex if it's needed (this step generates the index file)
makeindex refman.idx

# Run pdflatex again to generate the PDF (run it multiple times to resolve references)
pdflatex refman.tex
pdflatex refman.tex

# If a documentation has been generated, copy it to the main directory
if [ -f "refman.pdf" ]; then cp refman.pdf /doxy/documentation.pdf; fi
