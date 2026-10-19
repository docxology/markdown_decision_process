"""Corrected source assembly keeps prior-publication identity separate."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("paper_assembly",ROOT/"paper/assemble_paper.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_markdown_and_validation_do_not_require_tex(tmp_path,monkeypatch):
    empty=tmp_path/"empty-bin"
    empty.mkdir()
    monkeypatch.setenv("PATH",str(empty))
    assembler=module.PaperAssembler(output_dir=str(tmp_path/"out"))
    assert assembler._check_dependencies("markdown")
    assert assembler._check_dependencies("validate")
    assert not assembler._check_dependencies("pdf")


def test_revised_assembly_is_a_draft_without_reasserting_old_version_doi(tmp_path):
    assembler=module.PaperAssembler(paper_dir=str(ROOT/"paper"),output_dir=str(tmp_path/"out"))
    assert assembler.validate_sections()
    output=assembler.create_markdown_paper()
    text=Path(output).read_text()
    assert 'status: "corrected source draft; not a new deposit"' in text
    assert 'related-publication-doi: "10.5281/zenodo.17244387"' in text
    assert 'Historical publication DOI' in text
    assert 'Evaluation Protocol and Evidence' in text

    front_matter = text.split("---", 2)[1]
    assert "Those values and their interpretations are withdrawn" in front_matter
    assert "revolutionizes document processing" not in front_matter
