# Project Aegis CLI

[![Python CI](https://github.com/JamesTheGiblet/Project-Aegis-CLI/actions/workflows/python-ci.yml/badge.svg)](https://github.com/JamesTheGiblet/Project-Aegis-CLI/actions/workflows/python-ci.yml)
[![PyPI version](https://badge.fury.io/py/praximous-aegis-cli.svg)](https://badge.fury.io/py/praximous-aegis-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple command-line tool to automate the generation of essential security documentation for your projects.

## The Problem

Every good project needs a `SECURITY.md` file, a `dependabot.yml` config, and basic security guidelines. But let's be honest—it’s a boring, repetitive chore that's easy to forget. So, most projects don't have them until it's too late.

## The Solution

`aegis` is a simple command-line tool that does the grunt work for you. It scans your project, figures out what language you're using, and generates those essential security starter files. It turns a 15-minute chore into a 3-second command.

## Disclaimer: Read This First

Let's be crystal clear: **this tool is a starting point, not a magic bullet.** It generates boilerplate security documentation based on best practices. It is **NOT** a vulnerability scanner, a security audit tool, or a replacement for a real security strategy. You still need to do the hard work of writing secure code and using dedicated security tools.

## Features

* **Language Detection**: Scans your project to figure out what you're building with (currently supports Python and JavaScript).
* **Generates Essential Files**: Automatically creates the following from best-practice templates:
  * `.github/dependabot.yml`: A ready-to-use config to keep your dependencies updated via GitHub.
  * `security/SECURITY.md`: A solid, customizable policy for how to report vulnerabilities.
  * `security/SecureCodingGuide.md`: A language-specific checklist of common-sense security practices.
* **Safe and Customizable**: Use the `--dry-run` flag to preview changes and `--output` to specify a custom directory.

## Installation

Install from PyPI:

```bash
pip install praximous-aegis-cli
```

Or, to contribute, clone the repo and install in editable mode:

```bash
git clone https://github.com/JamesTheGiblet/Project-Aegis-CLI.git
cd Project-Aegis-CLI
pip install -e .[test]
```

## How to Use It

Navigate to your project directory and run the command. `aegis` will detect the language and generate the files.

```bash
aegis /path/to/your/project
```

### Options

* `--output <directory>`: Put the generated `SECURITY.md` and `SecureCodingGuide.md` files somewhere else.
* `--verbose`: See the full scan report as it runs.
* `--dry-run`: See what the tool would do without actually writing any files.

## The Roadmap

*Perfect is the enemy of shipped*, but here's what's next:

* Support for more languages (Java, Go, Rust).
* Optional integration with tools like Snyk or OSV.
* Better dynamic customization of the generated files.

## Want to Go Deeper?

The free tool gets you started with the basics. But if you want to learn about industry-grade security strategies, penetration testing, and building a secure development lifecycle (SDLC), I'm putting together a comprehensive guide. You can find out more at jamesthegiblet.co.uk.

## License

This project is licensed under the MIT License.

---
*Stop neglecting the basics. The code is the proof, and good security docs are part of that proof.*
