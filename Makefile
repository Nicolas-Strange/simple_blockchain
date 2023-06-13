# Makefile

.PHONY: install_requirements
install_requirements:
	pip install --upgrade pip
	pip install -r requirements.txt
