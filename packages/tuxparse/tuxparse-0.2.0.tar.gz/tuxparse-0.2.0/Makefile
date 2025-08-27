all: test typecheck style flake8

TUXPKG_MIN_COVERAGE = 97.48

export PROJECT := tuxparse

all: test flake8 style

include $(shell tuxpkg get-makefile)

stylecheck: style flake8
