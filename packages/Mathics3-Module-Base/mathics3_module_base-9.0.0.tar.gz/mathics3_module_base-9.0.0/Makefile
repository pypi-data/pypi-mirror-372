# A GNU Makefile to run various tasks - compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= admin-tools/git2cl
PYTHON ?= python3
PIP ?= pip3
BASH ?= bash
RM  ?= rm
PYTEST_OPTIONS ?=
DOCTEST_OPTIONS ?=

# Variable indicating Mathics3 Modules you have available on your system, in latex2doc option format
MATHICS3_MODULE_OPTION ?= --load-module pymathics.graph,pymathics.natlang

.PHONY: \
   all \
   clean \
   develop \
   dist \
   rmChangeLog \
   ChangeLog

#: Default target - same as "develop"
all: develop

develop:
	$(PIP) install -e .[dev]

# See note above on ./setup.py
#: Set up to run from the source tree with full dependencies and Cython
develop-full-cython: mathics/data/op-tables.json mathics/data/operators.json
	$(PIP) install -e .[dev,full,cython]


#: Make distribution: wheel and tarball
dist:
	./admin-tools/make-dist.sh

#: Install Mathics-Module-Base
install:
	$(PIP) install -e .


#: Clean up temporary files
clean:
	find . | grep -E '\.pyc' | xargs rm -rvf;
	find . | grep -E '\.pyo' | xargs rm -rvf;
	$(PYTHON) ./setup.py $@

#: Remove ChangeLog
rmChangeLog:
	$(RM) ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@
	patch ChangeLog < ChangeLog-spell-corrected.diff
