import re
from pathlib import Path

import nbformat
import numpy as np

from gpap2.io import read_contract_csv
from gpap2.notebook_reporting import (
    build_feature_contract_table,
    build_input_contract_table,
    build_model_contract_table,
    build_quality_gate_table,
    build_transformation_contract_table,
)
from gpap2.preprocessing import prepare_national_features
from gpap2.validation import validate_cohort_relationships, validate_contract_directory


def test_runtime_method_tables_expose_the_locked_contract(
    repository_root: Path, reference_config
) -> None:
    contracts = read_contract_csv(reference_config.resolve(reference_config.contracts_file))
    validation = validate_contract_directory(
        reference_config.resolve(reference_config.input_directory),
        reference_config.resolve(reference_config.contracts_file),
        reference_config,
    )
    cohorts = validate_cohort_relationships(
        reference_config.resolve(reference_config.input_directory), reference_config
    )
    identity = build_input_contract_table(reference_config, contracts, validation)
    quality = build_quality_gate_table(validation, cohorts)
    assert identity["rows"].tolist() == [6067, 3020, 1456]
    assert identity["numeric_features"].tolist() == [14, 17, 21]
    assert identity["sha256"].str.fullmatch(r"[A-F0-9]{64}").all()
    assert identity["feature_names_in_order"].str.contains("gpad_1_day_share").all()
    assert identity["feature_names_in_order"].str.contains("gpad_2_to_7_days_share").all()
    assert quality["passed"].all()

    matrix = read_contract_csv(
        repository_root / "data/reference/primary_practice_access_clustering_matrix.csv"
    )
    prepared = prepare_national_features(matrix, reference_config)
    features = build_feature_contract_table(reference_config, "national_14")
    transformations = build_transformation_contract_table(prepared)
    model = build_model_contract_table(reference_config, prepared)
    assert features["feature"].tolist() == list(prepared.feature_names)
    assert features.loc[features["transformation"].eq("log1p"), "feature"].tolist() == list(
        reference_config.specification("national_14").log1p_features
    )
    assert transformations["iqr_gate_passed"].all()
    assert np.all(transformations["pre_scaling_iqr"] > 0)
    assert model.set_index("setting").loc["identifier use", "value"].startswith("traceability")


def test_notebooks_one_to_four_show_generated_method_contracts(repository_root: Path) -> None:
    notebook_paths = sorted((repository_root / "notebooks").glob("0[1-4]_*.ipynb"))
    assert len(notebook_paths) == 4
    forbidden_code_literals = (
        "0.5236133527826328",
        "0.894915323255533",
        "0.24868476416596344",
        "892AFAF3EC4CEB9D6B1D7DC659580CE3E11C8809ED7D792A87AA7DC8BA67FDD3",
        "8E2B9618DE15BB363EA28F2946F7DDBD530845AC413507265D7450EFA137376C",
    )
    for path in notebook_paths:
        notebook = nbformat.read(path, as_version=4)
        markdown = "\n".join(
            cell.source for cell in notebook.cells if cell.cell_type == "markdown"
        )
        code = "\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
        assert "## Method contract" in markdown
        assert "Stage handover" in markdown
        assert "gpap2.notebook_reporting" in code
        assert "build_output_contract_table" in code or "build_comparison_contract_table" in code
        assert not any(literal in code for literal in forbidden_code_literals)
        assert "13-feature" not in markdown
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", markdown):
            if re.match(r"^[a-z]+://", target):
                continue
            assert (path.parent / target).resolve().exists(), f"broken notebook link: {target}"
