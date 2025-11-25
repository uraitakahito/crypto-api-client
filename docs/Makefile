# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXINTL    ?= sphinx-intl
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile gettext update-po html-ja html-all

# Generate pot files for translation
gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext" $(SPHINXOPTS) $(O)

# Update po files for Japanese translation
update-po: gettext
	@$(SPHINXINTL) update -p "$(BUILDDIR)/gettext" -d "$(SOURCEDIR)/locale" -l ja

# Build Japanese HTML documentation
html-ja:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)/ja" -D language=ja $(SPHINXOPTS) $(O)

# Build all languages
html-all: html html-ja

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
