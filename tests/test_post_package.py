from cine_skills.post_package import validate_post_package
from tests.post_fixtures import post_index, write_post_package

def test_valid_post_package_has_exact_inventory(tmp_path, repository_root):
    assert validate_post_package(write_post_package(tmp_path / "post"), repository_root, post_index()) == []

def test_post_package_rejects_extra_entry(tmp_path, repository_root):
    errors = validate_post_package(write_post_package(tmp_path / "post", extra="notes.txt"), repository_root, post_index())
    assert any("unexpected entry" in error for error in errors)

def test_post_package_rejects_project_mismatch(tmp_path, repository_root):
    package = write_post_package(tmp_path / "post")
    (package / "edit-plan.json").write_text('{"project_id":"OTHER"}', encoding="utf-8")
    assert validate_post_package(package, repository_root, post_index())

def test_post_package_requires_edit_plan_unit_as_canonical_for_every_plan(tmp_path, repository_root):
    package = write_post_package(tmp_path / "post")
    import json
    path = package / "color-plan.json"
    payload = json.loads(path.read_text())
    payload["unit_id"] = "NINEL-U02"
    path.write_text(json.dumps(payload), encoding="utf-8")
    from dataclasses import replace
    errors = validate_post_package(package, repository_root, replace(post_index(), unit_ids=frozenset({"NINEL-U01", "NINEL-U02"})))
    assert any("NINEL-U02" in error for error in errors)

def test_post_package_rejects_mixed_units_inside_source_context(tmp_path, repository_root):
    package = write_post_package(tmp_path / "post")
    import json
    path = package / "color-plan.json"
    payload = json.loads(path.read_text())
    payload["source_context"]["edit_segments"][0]["segment_id"] = "NINEL-U02-ED001"
    path.write_text(json.dumps(payload), encoding="utf-8")
    from dataclasses import replace
    errors = validate_post_package(package, repository_root, replace(post_index(), shot_ids=frozenset({"NINEL-U01-S01-SH001"}), media_ids=frozenset({"NINEL-MD001"})))
    assert any("NINEL-U02" in error for error in errors)

def test_post_package_rejects_uncovered_upstream_edit_segment(tmp_path, repository_root):
    package = write_post_package(tmp_path / "post")
    import json
    path = package / "sound-post-plan.json"
    payload = json.loads(path.read_text())
    payload["source_context"]["edit_segments"] = [payload["source_context"]["edit_segments"][0]]
    for item in payload["items"]:
        item["edit_segment_ids"] = ["NINEL-U01-ED001"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    from dataclasses import replace
    errors = validate_post_package(package, repository_root, replace(post_index(), edit_segment_ids=frozenset({"NINEL-U01-ED001", "NINEL-U01-ED002"})))
    assert any("missing coverage for upstream edit segment NINEL-U01-ED002" in error for error in errors)

def test_post_package_rejects_unknown_nested_shot_and_media_references(tmp_path, repository_root):
    package = write_post_package(tmp_path / "post")
    from dataclasses import replace
    errors = validate_post_package(package, repository_root, replace(post_index(), shot_ids=frozenset(), media_ids=frozenset()))
    assert any("unknown upstream shot NINEL-U01-S01-SH001" in error for error in errors)
    assert any("unknown upstream media NINEL-MD001" in error for error in errors)
