#!/bin/sh
# Generate config if not present and generate documentation
cd /doxy/docs
if [ ! -f "Doxyfile" ]; then doxygen -g; fi
doxygen Doxyfile 1> /dev/null

# Generate pdf from tex
cd /doxy/docs/latex 1> /dev/null

# Run pdflatex to compile the TeX files into a PDF
pdflatex refman.tex 1> /dev/null

# Run makeindex if it's needed (this step generates the index file)
makeindex refman.idx 1> /dev/null

# Run pdflatex again to generate the PDF (run it multiple times to resolve references)
pdflatex refman.tex 1> /dev/null
pdflatex refman.tex 1> /dev/null

# If a documentation has been generated, copy it to the main directory
if [ -f "refman.pdf" ]; then cp refman.pdf /doxy/docs/documentation.pdf 1> /dev/null; fi
