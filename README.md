# Cameron Severn — Resume

[![Build resume](https://github.com/cameronsevern/resume/actions/workflows/build.yml/badge.svg)](https://github.com/cameronsevern/resume/actions/workflows/build.yml)

I am a scientist and technologist working across software engineering, statistical machine learning, production systems, and agentic AI. This repository contains the public, reproducible version of my resume.

- [View the current PDF](./output/pdf/cameron-severn-resume.pdf)
- [Read the Markdown source](./resume.md)
- [Explore selected engineering work](./PROJECTS.md)
- [Review selected research and intellectual property](./RESEARCH.md)
- [Connect on LinkedIn](https://www.linkedin.com/in/cameron-severn-54b0b76b/)

## What this repository demonstrates

The resume is maintained as Markdown, rendered with a small Python/ReportLab pipeline, and checked for page count, extractable text, and required content. GitHub Actions rebuilds and verifies it on every change.

The public repository intentionally contains only portfolio-ready material. Job-specific application strategy, source captures, and private working notes are maintained separately.

## Build locally

```sh
make setup
make resume
```

The generated file is `output/pdf/cameron-severn-resume.pdf`. Run `make verify` for the same structural checks used in automation.
