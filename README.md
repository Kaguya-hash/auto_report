# Auto Report

Auto Report is a Windows desktop application that turns a completed PDF questionnaire into a structured Word report. A user selects a PDF, the application reads its form fields, applies a set of configurable scoring rules, and produces a `.docx` report with the calculated values and the corresponding explanatory text.

The project began as a Java prototype and was later reimplemented in Python. Its current goal is to explore a clean workflow architecture and a rule engine that can support a future clinical reporting tool, developed in direct collaboration with a Swiss-based medical specialist.

> **Important:** This software is an early-stage research prototype. It is **not** a medical device, diagnostic system, or substitute for clinical judgement. It has not been clinically validated, certified, or approved for patient care. Every generated report must be reviewed by a qualified clinician before it is used for any purpose.

## Table of Contents

- [Why This Project Is Worth a Look](#why-this-project-is-worth-a-look)
- [How It Works](#how-it-works)
- [Configuration Without Code: the JSON Rule Engine](#configuration-without-code-the-json-rule-engine)
- [Current Status](#current-status)
- [Getting Started on Windows](#getting-started-on-windows)
- [First-Run Configuration](#first-run-configuration)
- [Using the Application](#using-the-application)
- [Project Layout](#project-layout)
- [Security and Privacy](#security-and-privacy)
- [Dependencies](#dependencies)
- [Development Notes](#development-notes)
- [Testing and Validation](#testing-and-validation)
- [Uninstalling](#uninstalling)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact-and-further-information)

## Why This Project Is Worth a Look

Two design choices make this codebase more interesting than a typical "read a PDF, write a Word doc" script:

- **The scoring logic lives outside the code.** The engine that reads a questionnaire and computes results (`engine.py`) has no built-in knowledge of any specific instrument, cut-off, or wording. All of that comes from a JSON configuration file. This means the clinical logic can be updated, corrected, or extended by editing a data file rather than the Python program — see [Configuration Without Code](#configuration-without-code-the-json-rule-engine) below.
- **It respects the person using it, not just the person coding it.** The end user only has to point the app at a PDF, choose an output folder, and click a button. There is no console, no arguments to remember, and no need to understand Python to run it day to day — the technical complexity is confined to the JSON configuration and the codebase, not the interface.

On top of that, the project keeps a few good engineering habits: the configuration is encrypted at rest, the PDF-reading/report-writing logic is separated from the GUI, and the Windows installer is fully portable (no administrator rights, no system-wide Python install).

## How It Works

1. The user opens the app and selects a completed questionnaire PDF.
2. The application extracts the PDF's form field values using `pypdf`.
3. A generic rule engine evaluates those values against the configured rules: derived variables, thresholds, conditional logic, and text responses.
4. The report builder assembles a Word document from the results using `python-docx`.
5. The finished `.docx` is written to the output folder the user chose.

```
PDF form fields → pypdf → rule engine (engine.py) → python-docx → report.docx
                              ↑
                    JSON rules (encrypted at rest)
```

## Configuration Without Code: the JSON Rule Engine

The most reusable part of this project is the idea that the *behavior* of the report — which values are read, how they combine, what thresholds mean, and what text they produce — is entirely described in a JSON configuration, not hard-coded into the engine. The engine only knows how to evaluate a fixed set of generic node types:

| Node type | Purpose |
|---|---|
| Constant | A fixed value used elsewhere in the rules |
| Reference | Points to a value extracted from the PDF or to another computed node |
| Condition | Simple conditional (if/else) logic |
| Switch | Multi-branch logic, similar to a case statement |
| Sum | Adds together a set of referenced values |
| Item group | Groups related items so they can be scored together |
| Threshold check | Compares a computed value against a cut-off |
| Text-only response | Attaches explanatory wording to a result, with no numeric value |

Because these are generic building blocks rather than instrument-specific code, a domain expert (with technical guidance) can change what gets calculated and what the report says by editing the JSON — without touching `engine.py` at all. This is the "programming by configuration" idea behind the project: the same engine can support a different questionnaire, a revised cut-off, or new report wording just by shipping a new configuration file.

To make the shape of this concrete, here is a simplified, non-clinical illustration of what a rule set can express (this is **not** the real configuration used by the app):

```json
{
  "variables": {
    "item_1": { "type": "reference", "source": "pdf_field_q1" },
    "item_2": { "type": "reference", "source": "pdf_field_q2" },
    "total_score": {
      "type": "sum",
      "of": ["item_1", "item_2"]
    },
    "result_level": {
      "type": "threshold_check",
      "value": "total_score",
      "cutoff": 10,
      "if_above": "high",
      "if_below_or_equal": "low"
    },
    "result_text": {
      "type": "switch",
      "on": "result_level",
      "cases": {
        "high": "Score is above the configured cut-off.",
        "low": "Score is within the expected range."
      }
    }
  }
}
```

The real configuration is considerably richer — it also carries the clinical wording and cut-offs used in the actual reports — which is why it is encrypted rather than kept as a plain file (see [Security and Privacy](#security-and-privacy)).

## Current Status

Requirements, scoring rules, report wording, and validation criteria are being refined together with the collaborating clinician. Treat the application as a development and research tool while that work continues. The current implementation covers:

- A small Windows desktop interface built with PySide6.
- Selection of a PDF containing completed form fields.
- Declarative calculation rules kept outside the Python engine.
- Encrypted storage of the configuration (clinical rules, cut-offs, item text).
- Generation of a structured Word report.

## Getting Started on Windows

### Option A — Portable installation (recommended)

1. Download or clone the repository.
2. Run `setup.bat`.
3. The installer downloads Python 3.11.9, installs the required dependencies under the application folder, and creates an **Auto Report** shortcut in the Start Menu and, when available, on the Desktop.
4. Open the application from the shortcut.

> **Windows security note:** Because `setup.bat` is a script downloaded from the internet, Windows may block it from running (SmartScreen or a "Windows protected your PC" message), or double-clicking it may simply appear to do nothing. If that happens:
> 1. Right-click `setup.bat` and choose **Properties**.
> 2. At the bottom of the **General** tab, tick **Unblock** (if present) and click **OK**.
> 3. Run `setup.bat` again. If Windows still shows a SmartScreen warning, choose **More info** and then **Run anyway**.
>
> This is expected behavior for an unsigned script from a new repository, not a sign that the file is broken.

The application is installed per user under:

```
%LOCALAPPDATA%\Programs\AutoReport
```

The installer needs an internet connection to download Python, the dependencies, and the application files from the configured GitHub repository. Administrator rights are not normally required.

### Option B — Existing Python installation

Use Python 3.11 or a compatible Python 3 version:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r programa\requirements.txt
python programa\app.py
```

## First-Run Configuration

The report builder needs two files in the repository's `data` folder:

- `secret_data.enc` — the encrypted JSON configuration.
- `.env` — the locally generated Fernet key used to decrypt it.

These are local configuration files and should never be shared or committed. If either is missing, the GUI will ask for the source JSON scheme file and generate both through `encrypt_secret.py`.

The normal path is simply to start the GUI, select the scheme file when prompted, and let the application create the configuration. For development or administration workflows that need to prepare it directly, call `build_key_data(...)` from `programa/encrypt_secret.py` (there is currently no standalone command-line entry point). This utility takes a plaintext JSON configuration, generates a new key, overwrites `data\.env`, and writes `data\secret_data.enc`. Keep the plaintext JSON and `.env` out of version control and restrict access to them, especially when they contain clinical rules or wording.

## Using the Application

1. Select the completed questionnaire PDF with **Browse...**.
2. Select an output folder.
3. Enter an output filename, without the extension.
4. Click **Generate Report**.
5. Review the resulting Word document carefully before using it.

The `.docx` extension is added automatically. The PDF is read locally — the application does not call out to a cloud service or a remote patient-record system.

## Project Layout

- `programa/app.py` — PySide6 graphical interface and input validation.
- `programa/build_report_program.py` — PDF reading and Word report generation.
- `programa/engine.py` — generic rule-evaluation engine.
- `programa/secure_config.py` — Fernet decryption and configuration loading.
- `programa/encrypt_secret.py` — local utility for encrypting a JSON configuration.
- `programa/validate_equivalence.py` — development-time comparison script from the Java-to-Python migration; requires legacy reference files and is not part of the normal user workflow.
- `programa/requirements.txt` — Python dependencies.
- `data/secret_data.enc` — encrypted configuration data. The plaintext clinical configuration must never be committed.
- `setup.bat` — Windows installer using a local embedded Python runtime.
- `uninstall.bat` — Windows uninstaller for the installation created by `setup.bat`.

## Security and Privacy

This project may be used around sensitive clinical information. Before handling real patient data, put in place appropriate hospital controls for access, storage, retention, backups, and auditability.

- Do not commit patient PDFs, generated reports, plaintext configuration, or `data\.env`.
- Do not place patient data in issue reports, screenshots, logs, or public repositories.
- The encrypted configuration protects its contents at rest, but anyone with access to both `secret_data.enc` and its key can decrypt it.
- The current prototype is not a complete security or compliance solution and has not been assessed against Swiss healthcare, hospital, or data-protection requirements.
- Verify that reports are written only to an approved location, and remove temporary or obsolete copies according to the responsible institution's policy.

## Dependencies

- [PySide6](https://pypi.org/project/PySide6/) — desktop GUI.
- [cryptography](https://pypi.org/project/cryptography/) — Fernet encryption.
- [pypdf](https://pypi.org/project/pypdf/) — reading PDF form fields.
- [python-docx](https://pypi.org/project/python-docx/) — creating Word documents.

Exact version constraints are maintained in `programa/requirements.txt`.

## Development Notes

The main public workflow is `build_report(pdf_path, output_path)` in `programa/build_report_program.py`. The generic `evaluate(...)` function in `programa/engine.py` supports the rule node types described in [Configuration Without Code](#configuration-without-code-the-json-rule-engine).

Clinical behavior should be changed in the configuration and reviewed with the collaborating clinician. Changes to scoring, cut-offs, derived variables, or report wording should be accompanied by test cases and documented validation evidence.

The migration validation script is retained as development history. It references legacy modules and plaintext files not included in the normal Python application, so it may require the original Java/Python comparison fixtures before it can run.

## Testing and Validation

Before considering a change usable:

1. Check that the application starts in a clean Python environment.
2. Test valid and invalid PDF paths and output folders.
3. Compare calculated values against clinician-approved examples, including boundary values and missing or unexpected answers.
4. Open generated `.docx` files and inspect both totals and explanatory text.
5. Record the version of the configuration used for each validation run.

Automated clinical validation is still a work in progress. Passing a software test does not establish clinical validity.

## Uninstalling

For a portable installation, run `uninstall.bat` from the installed application, or remove **Auto Report** from Windows **Settings > Apps > Installed apps**. The uninstaller removes the per-user installation and its shortcuts.

## Contributing

Keep changes focused and explain their effect on the clinical workflow. Contributions that modify rules, thresholds, extracted fields, or report text should include:

- The reason for the change.
- Updated examples or tests.
- Confirmation from the responsible domain expert where appropriate.
- Any effect on existing generated reports.

Please do not submit real patient data or confidential clinical material.

## License

No license file is currently included. Until a license is added, all rights remain with the copyright holder, and reuse should be agreed with the project owner.

## Contact and Further Information

This project is maintained as a research collaboration with a Swiss-based medical specialist. For questions about clinical interpretation, requirements, or validation, consult the responsible clinician and project owner. Technical implementation details are available in the `programa` source files.
