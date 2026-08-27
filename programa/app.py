import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)

from .encrypt_secret import build_key_data
from .build_report_program import build_report

CONFIG_ENC_FILE = Path(__file__).resolve().parent.parent / "data" / "secret_data.enc"
CONFIG_ENV = Path(__file__).resolve().parent.parent / "data" / ".env"


class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Report Generator")
        self.setMinimumWidth(480)

        # --- PDF path ---
        self.pdf_edit = QLineEdit()
        pdf_browse = QPushButton("Browse...")
        pdf_browse.clicked.connect(self.browse_pdf)

        # --- Output folder ---
        self.folder_edit = QLineEdit()
        folder_browse = QPushButton("Browse...")
        folder_browse.clicked.connect(self.browse_folder)

        # --- Output file name (no extension) ---
        self.name_edit = QLineEdit()

        # --- Submit ---
        submit_btn = QPushButton("Generate Report")
        submit_btn.clicked.connect(self.on_submit)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("PDF file:"))
        row1 = QHBoxLayout()
        row1.addWidget(self.pdf_edit)
        row1.addWidget(pdf_browse)
        layout.addLayout(row1)

        layout.addWidget(QLabel("Output folder:"))
        row2 = QHBoxLayout()
        row2.addWidget(self.folder_edit)
        row2.addWidget(folder_browse)
        layout.addLayout(row2)

        layout.addWidget(QLabel("Output file name (no extension):"))
        layout.addWidget(self.name_edit)

        layout.addWidget(submit_btn)

        self.setLayout(layout)

    def browse_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
        if path:
            self.pdf_edit.setText(path)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if path:
            self.folder_edit.setText(path)

    def browse_scheme_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select scheme file")
        if not path:
            return None
        return Path(path)

    def on_submit(self):
        pdf_path = Path(self.pdf_edit.text().strip())
        folder = Path(self.folder_edit.text().strip())
        name = self.name_edit.text().strip()

        if not pdf_path.is_file():
            QMessageBox.critical(self, "Error", "The given PDF file does not exist.")
            return
        if not folder.is_dir():
            QMessageBox.critical(self, "Error", "The given output folder does not exist.")
            return
        if not name:
            QMessageBox.critical(self, "Error", "Please provide an output file name.")
            return

        output_path = folder / f"{name}.docx"

        # If either config file is missing, ask for a scheme file and build them first.
        if not CONFIG_ENC_FILE.exists() or not CONFIG_ENV.exists():
            QMessageBox.information(
                self,
                "Configuration needed",
                "Configuration files were not found.\nPlease select a scheme file to generate them.",
            )
            scheme_path = self.browse_scheme_file()
            if scheme_path is None:
                QMessageBox.warning(self, "Cancelled", "No scheme file selected. Operation cancelled.")
                return
            try:
                build_key_data(scheme_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to build configuration data:\n{e}")
                return

        try:
            build_report(pdf_path, output_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build report:\n{e}")
            return

        QMessageBox.information(self, "Success", f"Report generated successfully at:\n{output_path}")


def main():
    app = QApplication(sys.argv)
    window = ReportWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()