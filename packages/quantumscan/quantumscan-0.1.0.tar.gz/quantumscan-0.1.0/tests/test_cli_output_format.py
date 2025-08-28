import importlib
import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace


def run_cli(args, cwd: Path):
    """Execute the CLI in-process for easier monkeypatching.

    Returns a namespace mimicking ``subprocess.CompletedProcess`` with
    ``returncode``, ``stdout`` and ``stderr`` attributes.
    """
    src = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src))
    module = importlib.reload(importlib.import_module("quantumscan.cli.__main__"))

    old_cwd = os.getcwd()
    buf_out, buf_err = io.StringIO(), io.StringIO()
    try:
        os.chdir(cwd)
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            try:
                code = module.main(args)
            except SystemExit as e:  # emulate subprocess return code
                code = int(e.code) if isinstance(e.code, int) else 1
    finally:
        os.chdir(old_cwd)
        sys.path.pop(0)

    return SimpleNamespace(returncode=code, stdout=buf_out.getvalue(), stderr=buf_err.getvalue())


def test_cli_outputs_expected_lines(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    (tmp_path / 'b.c').write_text('EVP_sha1();\n')
    (tmp_path / 'c.js').write_text("crypto.createHash('md5');\n")
    result = run_cli(['--path', '.'], tmp_path)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 3
    assert "a.py:1: RSA | token='RSA.generate'" in lines
    assert "b.c:1: SHA-1 | token='EVP_sha1('" in lines
    assert "c.js:1: MD5 | token='crypto.createHash('md5')'" in lines


def test_max_evidence_len_truncates(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    result = run_cli(['--path', '.', '--max-evidence-len', '10'], tmp_path)
    assert result.returncode == 0
    line = result.stdout.strip()
    assert "RSA.gen..." in line


def test_algo_filter(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\nECDH()\n')
    result = run_cli(['--path', '.', '--algo', 'ecc'], tmp_path)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 1
    assert lines[0].startswith('a.py:2: ECC')


def test_algo_filter_alias(tmp_path: Path):
    (tmp_path / 'a.py').write_text(
        'from cryptography.hazmat.primitives.asymmetric import ec\n'
        'ec.generate_private_key(ec.SECP256K1())\n'
    )
    result = run_cli(['--path', '.', '--algo', 'secp256k1'], tmp_path)
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert any(line.startswith('a.py:2: ECC') for line in lines)


def test_no_output_when_no_findings(tmp_path: Path):
    (tmp_path / 'a.py').write_text('# just a comment')
    result = run_cli(['--path', '.'], tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == ''


def test_report_option_writes_html(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    out = tmp_path / 'scan.html'
    result = run_cli(['--path', '.', '--report', str(out)], tmp_path)
    assert result.returncode == 0
    assert out.exists()
    text = out.read_text()
    assert '<section id="summary">' in text


def test_report_option_writes_pdf(tmp_path: Path, monkeypatch):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    out = tmp_path / 'scan.pdf'

    def fake_generate(html: str, output_path: str) -> bool:
        Path(output_path).write_text('PDF')
        return True

    monkeypatch.setattr('quantumscan.reporting.pdf.generate_pdf', fake_generate)
    result = run_cli(['--path', '.', '--report', str(out), '--format', 'pdf'], tmp_path)
    assert result.returncode == 0
    assert out.exists()


def test_unknown_format_fails(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    result = run_cli(['--path', '.', '--report', 'out.txt', '--format', 'txt'], tmp_path)
    assert result.returncode != 0


def test_report_markdown_with_output(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    out = tmp_path / 'scan.md'
    result = run_cli(['--path', '.', '--report', 'markdown', '--output', str(out)], tmp_path)
    assert result.returncode == 0
    assert out.exists()
    text = out.read_text()
    assert 'RSA' in text


def test_report_markdown_requires_output(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    result = run_cli(['--path', '.', '--report', 'markdown'], tmp_path)
    assert result.returncode != 0
    assert '--output required' in result.stderr


def test_pdf_generate_fallback(tmp_path: Path, monkeypatch):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)\n')
    out = tmp_path / 'scan.pdf'

    def fake_generate(html: str, output_path: str) -> bool:
        return False

    monkeypatch.setattr('quantumscan.reporting.pdf.generate_pdf', fake_generate)
    result = run_cli(['--path', '.', '--report', str(out), '--format', 'pdf'], tmp_path)
    # PDF generation fails -> HTML written
    assert result.returncode == 0
    assert 'WARN weasyprint missing' in result.stderr
