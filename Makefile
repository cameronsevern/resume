PYTHON ?= .venv/bin/python
RESUME_MD := resume.md
RESUME_PDF := output/pdf/cameron-severn-resume.pdf

.PHONY: setup resume verify clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

resume: $(RESUME_PDF)

$(RESUME_PDF): $(RESUME_MD) scripts/render_resume.py
	$(PYTHON) scripts/render_resume.py $(RESUME_MD) $(RESUME_PDF)
	$(PYTHON) scripts/verify_pdf.py $(RESUME_PDF) --max-pages 2 --require "Cameron Severn"

verify: resume
	$(PYTHON) scripts/verify_pdf.py $(RESUME_PDF) --max-pages 2 --require "Cameron Severn" --require "Scientist and technologist"

clean:
	rm -f output/pdf/cameron-severn-resume.pdf
