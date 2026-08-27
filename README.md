# Auto Report

Auto Report is an experimental Python desktop application for a Swiss hospital workflow. It helps a clinician turn a completed PDF questionnaire into a structured Word report by reading the PDF form fields, applying configurable scoring rules, and inserting the resulting values and explanatory text into a `.docx` document.

The project began as a Java desktop prototype and has since been reimplemented in Python. Its purpose is to explore workflow architecture, domain-aligned calculation logic, and a lightweight foundation for a future clinical reporting tool.

> **Important:** This software is an early-stage research prototype. It is not a medical device, diagnostic system, or substitute for clinical judgement. It has not been clinically validated, certified, or approved for patient care. Generated reports must be reviewed by a qualified clinician before they are used for any purpose.

## Current Status

Requirements, scoring rules, report wording, and validation criteria are being refined through direct collaboration with a Swiss-based medical specialist. The application should be treated as a development and research tool while that work continues.

The current implementation focuses on:

- A small Windows desktop interface built with PySide6.
- Selection of a PDF containing completed form fields.
- Declarative calculation rules kept outside the Python engine.
- Encrypted storage of the configuration containing clinical rules, cut-offs, and item text.
- Generation of a structured Word report.

## How It Works

1. The user selects a completed PDF in the graphical interface.
2. The application extracts the PDF form values using `pypdf`.
3. The generic rule engine evaluates the configured values, derived variables, thresholds, and text responses.
4. The report builder creates a Word document using `python-docx`.
5. The generated `.docx` is saved in the output folder selected by the user.

The calculation engine intentionally does not contain instrument-specific clinical knowledge. The relevant rules and wording are loaded from encrypted configuration so that domain changes can be made without rewriting the generic evaluator.

## Project Layout

- `programa/app.py` - PySide6 graphical interface and input validation.
- `programa/build_report_program.py` - PDF reading and Word report generation.
- `programa/engine.py` - Generic rule-evaluation engine.
- `programa/secure_config.py` - Fernet decryption and configuration loading.
- `programa/encrypt_secret.py` - Local utility for encrypting a JSON configuration.
- `programa/validate_equivalence.py` - Development-time comparison script from the Java-to-Python migration; it requires legacy reference files and is not part of the normal user workflow.
- `programa/requirements.txt` - Python dependencies.
- `data/secret_data.enc` - Encrypted configuration data. The plaintext clinical configuration must never be committed.
- `setup.bat` - Windows installer using a local embedded Python runtime.
- `uninstall.bat` - Windows uninstaller for the installation created by `setup.bat`.

## Quick Start on Windows

### Option A: Portable installation

This is the intended option for users who want a self-contained installation:

1. Download or clone the repository.
2. Run `setup.bat`.
3. The installer downloads Python 3.11.9, installs the dependencies under the application folder, and creates an **Auto Report** shortcut in the Start Menu and, when available, on the Desktop.
4. Open the application from the shortcut.

The application is installed per user under:

```text
%LOCALAPPDATA%\Programs\AutoReport
```

The installer needs an internet connection to download Python, dependencies, and the application files from the configured GitHub repository. Windows administrator rights are not normally required.

### Option B: Existing Python installation

Use Python 3.11 or a compatible Python 3 version, then run:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r programa\requirements.txt
python programa\app.py
```

The GUI can also be launched with the Python executable directly:

```bat
python programa\app.py
```

## First-Run Configuration

The report builder needs two files in the repository's `data` folder:

- `secret_data.enc` - the encrypted JSON configuration.
- `.env` - the locally generated Fernet key used to decrypt it.

These files are deliberately treated as local configuration and should not be shared or committed. If either file is missing, the GUI asks for the source JSON scheme file and generates both files through `encrypt_secret.py`.

The normal setup path is to start the GUI, select the scheme file when prompted, and let the application create the configuration. For development or administration code that needs to prepare it directly, call `build_key_data(...)` from `programa/encrypt_secret.py`; the module does not currently provide a standalone command-line entry point. The utility expects a plaintext JSON configuration, generates a new key, overwrites `data\.env`, and writes `data\secret_data.enc`. Keep the plaintext JSON and `.env` out of version control and restrict access to them appropriately, especially when they contain clinical rules or wording.

## Using the Application

1. Select the completed questionnaire PDF with **Browse...**.
2. Select an output folder.
3. Enter an output filename without the extension.
4. Select **Generate Report**.
5. Review the resulting Word document carefully before using it.

The output filename receives the `.docx` extension automatically. The input PDF is read locally; the application does not provide a cloud service or a remote patient-record integration.

## Security and Privacy

This project may be used around sensitive clinical information. Before handling real patient data, establish appropriate hospital controls for access, storage, retention, backups, and auditability.

- Do not commit patient PDFs, generated reports, plaintext configuration, or `data\.env`.
- Do not place patient data in issue reports, screenshots, logs, or public repositories.
- The encrypted configuration protects its contents at rest, but anyone who can access both `secret_data.enc` and its key can decrypt it.
- The current prototype is not a complete security or compliance solution and has not been assessed against Swiss healthcare, hospital, or data-protection requirements.
- Verify that reports are written only to an approved location and remove temporary or obsolete copies according to the responsible institution's policy.

## Dependencies

The application uses:

- [PySide6](https://pypi.org/project/PySide6/) for the desktop GUI.
- [cryptography](https://pypi.org/project/cryptography/) for Fernet encryption.
- [pypdf](https://pypi.org/project/pypdf/) for reading PDF form fields.
- [python-docx](https://pypi.org/project/python-docx/) for creating Word documents.

Exact version constraints are maintained in `programa/requirements.txt`.

## Development Notes

The main public workflow is `build_report(pdf_path, output_path)` in `programa/build_report_program.py`. The generic `evaluate(...)` function in `programa/engine.py` supports rule nodes such as constants, references, conditions, switches, sums, item groups, threshold checks, and text-only responses.

Clinical behavior should be changed in the configuration and reviewed with the collaborating clinician. Changes to scoring, cut-offs, derived variables, or report wording should be accompanied by test cases and documented validation evidence.

The migration validation script is retained as development history. It references legacy modules and plaintext files that are not included in the normal Python application, so it may require the original Java/Python comparison fixtures before it can run.

## Testing and Validation

Before considering a change usable:

1. Check that the application starts in a clean Python environment.
2. Test valid and invalid PDF paths and output folders.
3. Compare calculated values against clinician-approved examples, including boundary values and missing or unexpected answers.
4. Open generated `.docx` files and inspect both totals and explanatory text.
5. Record the version of the configuration used for each validation run.

Automated clinical validation is still a work in progress. Passing a software test does not establish clinical validity.

## Uninstalling

For a portable installation, run `uninstall.bat` from the installed application or remove **Auto Report** from Windows **Settings > Apps > Installed apps**. The uninstaller removes the per-user installation and its shortcuts.

## Contributing

Keep changes focused and explain their effect on the clinical workflow. Contributions that modify rules, thresholds, extracted fields, or report text should include:

- The reason for the change.
- Updated examples or tests.
- Confirmation from the responsible domain expert where appropriate.
- Any effect on existing generated reports.

Please do not submit real patient data or confidential clinical material.

## License

No license file is currently included. Until a license is added, all rights remain with the copyright holder and reuse should be agreed with the project owner.

## Contact and Further Information

This project is maintained as a research collaboration with a Swiss-based medical specialist. For questions about clinical interpretation, requirements, or validation, consult the responsible clinician and project owner. Technical implementation details are available in the `programa` source files.
