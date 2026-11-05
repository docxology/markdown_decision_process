"""Corrected source assembly keeps prior-publication identity separate."""
import importlib.util
import shutil
from pathlib import Path

import pytest

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


@pytest.fixture(scope="module")
def assembled_draft(tmp_path_factory):
    """Read the actual manuscript and write both text formats outside the tree."""
    output = tmp_path_factory.mktemp("corrected-draft")
    assembler = module.PaperAssembler(
        paper_dir=str(ROOT / "paper"), output_dir=str(output)
    )
    assert assembler.validate_sections()
    return {
        "markdown": Path(assembler.create_markdown_paper()).read_text(encoding="utf-8"),
        "latex_markdown": Path(assembler.create_latex_compatible_markdown()).read_text(
            encoding="utf-8"
        ),
    }


@pytest.mark.parametrize("format_name", ["markdown", "latex_markdown"])
def test_assembled_draft_retains_the_evidence_review(assembled_draft, format_name):
    text = assembled_draft[format_name]
    assert "# Evaluation evidence review" in text
    assert "GPT-2 identity" in text
    assert "ec902bb5661b3741b2b802ab37ee4469d8369318" in text
    assert (
        "Neither historical provenance nor broad scientific validity is marked resolved"
        in text
    )
    assert 'status: "corrected source draft; not a new deposit"' in text
    assert 'related-publication-doi: "10.5281/zenodo.17244387"' in text
    assert '\ndoi:' not in text.split("---", 2)[1]


@pytest.mark.parametrize(
    "withdrawn_claim",
    [
        "First comprehensive application of MDP/POMDP theory",
        "learning optimal transformation policies",
        "provides calibrated probability distributions over semantic interpretations",
        "MDP provides comparable performance for structured document tasks",
        "providing theoretical guarantees and principled uncertainty handling",
        "based on current limitations, empirical evidence, and theoretical opportunities",
        "How can we maintain theoretical guarantees",
    ],
)
def test_active_draft_does_not_reassert_withdrawn_comparisons(
    assembled_draft, withdrawn_claim
):
    # The abstract already withdraws these claims. Check the complete body too;
    # discussion of future calibration/optimality remains appropriate.
    for format_name, text in assembled_draft.items():
        assert withdrawn_claim.casefold() not in text.casefold(), format_name


@pytest.mark.parametrize("review_state", ["missing", "empty"])
def test_validation_requires_the_evidence_review(tmp_path, review_state):
    paper = tmp_path / "paper"
    paper.mkdir()
    for source in (ROOT / "paper").glob("*.md"):
        shutil.copyfile(source, paper / source.name)
    review = paper / "EVALUATION_EVIDENCE.md"
    if review_state == "missing":
        review.unlink()
    else:
        review.write_text("\n", encoding="utf-8")
    assembler = module.PaperAssembler(
        paper_dir=str(paper), output_dir=str(tmp_path / "out")
    )
    assert not assembler.validate_sections()


@pytest.mark.parametrize(
    "method_name", ["create_markdown_paper", "create_latex_compatible_markdown"]
)
@pytest.mark.parametrize("review_state", ["missing", "empty"])
def test_direct_text_assembly_requires_the_evidence_review(
    tmp_path, method_name, review_state
):
    paper = tmp_path / "paper"
    paper.mkdir()
    for source in (ROOT / "paper").glob("*.md"):
        shutil.copyfile(source, paper / source.name)
    review = paper / "EVALUATION_EVIDENCE.md"
    if review_state == "missing":
        review.unlink()
    else:
        review.write_text("\n", encoding="utf-8")
    output = tmp_path / "out"
    assembler = module.PaperAssembler(paper_dir=str(paper), output_dir=str(output))
    with pytest.raises(ValueError, match="EVALUATION_EVIDENCE"):
        getattr(assembler, method_name)()
    assert not (output / "mdp_paper.md").exists()
    assert not (output / "mdp_paper_latex.md").exists()
