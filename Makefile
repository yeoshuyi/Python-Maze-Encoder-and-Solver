ifeq ($(OS),Windows_NT)
    PYTHON = python
    RM = del /Q
    FIX_PATH = $(subst /,\,$1)
    VENV_BIN = .venv\Scripts\activate
else
    PYTHON = python3
    RM = rm -rf
    FIX_PATH = $1
    VENV_BIN = ./.venv/bin/activate
endif

.PHONY: help setup encode solve clean

help:
	@echo "Usage:"
	@echo "  make setup   - Create venv and install requirements"
	@echo "  make encode  - Generate maze_v2.bin from maze.png"
	@echo "  make solve   - Generate maze_v2.gif from maze_v2.bin"
	@echo "  make clean   - Remove temporary files and venv"

setup:
	$(PYTHON) -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt

encode:
	cd src && $(PYTHON) maze_encoderv2.py

solve:
	cd src && $(PYTHON) maze_solverv2.py

clean:
	$(RM) src/__pycache__
	$(RM) .venv