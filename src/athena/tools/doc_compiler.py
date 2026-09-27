"""
Universal Academic Document Compiler for Athena.
Wraps Pandoc to convert Markdown to DOCX.
"""
import subprocess
import time
from pathlib import Path
from typing import Any

PANDOC_PATH = "/opt/homebrew/bin/pandoc"

class DocCompiler:
    """Document compilation engine using Pandoc."""

    def __init__(self, pandoc_path: str = PANDOC_PATH):
        self.pandoc_path = pandoc_path

    def validate_pandoc(self) -> str:
        """Check that Pandoc is installed and return its version string."""
        try:
            result = subprocess.run(
                [self.pandoc_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    def list_formats(self) -> list[str]:
        """Return supported output formats from Pandoc."""
        try:
            result = subprocess.run(
                [self.pandoc_path, "--list-output-formats"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def compile(
        self,
        input_path: str | Path,
        output_path: str | Path,
        template_path: str | Path | None = None,
        toc: bool = False,
        csl_path: str | Path | None = None,
        bib_path: str | Path | None = None,
        extra_args: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Compile markdown source to .docx using Pandoc.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        start_time = time.time()

        if not input_path.exists():
            return {
                "output_path": str(output_path),
                "file_size": 0,
                "elapsed_seconds": time.time() - start_time,
                "success": False,
                "warnings": f"Input file not found: {input_path}"
            }

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [self.pandoc_path, str(input_path), "-o", str(output_path)]

        if template_path:
            cmd.extend(["--reference-doc", str(template_path)])

        if toc:
            cmd.append("--toc")

        if bib_path:
            cmd.extend(["--bibliography", str(bib_path)])
            cmd.append("--citeproc")

            if csl_path:
                cmd.extend(["--csl", str(csl_path)])

        if extra_args:
            cmd.extend(extra_args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            elapsed = time.time() - start_time
            success = result.returncode == 0
            file_size = output_path.stat().st_size if output_path.exists() else 0

            return {
                "output_path": str(output_path),
                "file_size": file_size,
                "elapsed_seconds": elapsed,
                "success": success,
                "warnings": result.stderr.strip()
            }

        except Exception as e:
            return {
                "output_path": str(output_path),
                "file_size": 0,
                "elapsed_seconds": time.time() - start_time,
                "success": False,
                "warnings": str(e)
            }

    def compile_batch(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        template_path: str | Path | None = None
    ) -> dict[str, dict[str, Any]]:
        """Compile all .md files in a directory."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        results: dict[str, dict[str, Any]] = {}
        if not input_dir.exists() or not input_dir.is_dir():
            return results

        output_dir.mkdir(parents=True, exist_ok=True)

        for md_file in input_dir.glob("*.md"):
            out_file = output_dir / md_file.with_suffix(".docx").name
            res = self.compile(
                input_path=md_file,
                output_path=out_file,
                template_path=template_path
            )
            results[str(md_file)] = res

        return results
