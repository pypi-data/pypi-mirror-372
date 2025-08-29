# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
HTMLDIR       = ../html  # Changed from _build to ../html

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(HTMLDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean

# Custom clean target for our HTML directory
clean:
	rm -rf "$(HTMLDIR)/*"

# Custom HTML target with clean before build
html: clean
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(HTMLDIR)" $(SPHINXOPTS) $(O)
	@echo "HTML documentation built in $(HTMLDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(HTMLDIR)" $(SPHINXOPTS) $(O)