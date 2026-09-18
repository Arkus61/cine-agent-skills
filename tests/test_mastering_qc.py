import copy

from cine_skills.artifacts import validate_artifact


REQUIRED_CATEGORIES = (
    "video-resolution",
    "frame-rate",
    "aspect-ratio",
    "duration",
    "audio-channel-count",
    "audio-channel-layout",
    "av-sync",
    "missing-frames",
    "duplicate-frames",
    "black-frames",
    "video-levels",
    "audio-clipping",
    "audio-sample-peak",
    "audio-true-peak",
    "audio-loudness",
    "captions-presence",
    "captions-accuracy",
    "titles-presence",
    "title-safe",
    "title-readability",
    "compression-artifacts",
    "vfx-completion",
    "color-completion",
    "deliverable-integrity",
)


EXPECTED = {
    "video-resolution": ("equals", "1920x1080", "pixels"),
    "frame-rate": ("equals", 24, "fps"),
    "aspect-ratio": ("equals", "16:9", "ratio"),
    "duration": ("equals", 60, "seconds"),
    "audio-channel-count": ("equals", 2, "channels"),
    "audio-channel-layout": ("equals", "L,R", "layout"),
    "av-sync": ("review", "synchronous", None),
    "missing-frames": ("absent", False, None),
    "duplicate-frames": ("absent", False, None),
    "black-frames": ("review", "Only intentional black is present", None),
    "video-levels": ("review", "Conforms to the supplied delivery specification", None),
    "audio-clipping": ("absent", False, None),
    "audio-sample-peak": ("less-than-or-equal", -2, "dBFS"),
    "audio-true-peak": ("review", "Supply the delivery threshold", "dBTP"),
    "audio-loudness": ("review", "Supply the delivery target", "LUFS"),
    "captions-presence": ("present", True, None),
    "captions-accuracy": ("review", "RU captions match speech and relevant nonspeech audio", None),
    "titles-presence": ("present", True, None),
    "title-safe": ("review", "Opening title is readable within the supplied safe area", None),
    "title-readability": ("review", "Opening title is legible at intended display size", None),
    "compression-artifacts": ("absent", False, None),
    "vfx-completion": ("review", "No temporary or incomplete VFX remains", None),
    "color-completion": ("review", "Current color output is reviewed for the delivery display", None),
    "deliverable-integrity": ("review", "Required deliverables open and correspond to the current master", None),
}


MEASUREMENT_CATEGORIES = {
    "video-resolution",
    "frame-rate",
    "aspect-ratio",
    "duration",
    "audio-channel-count",
    "audio-channel-layout",
    "audio-sample-peak",
    "audio-true-peak",
    "audio-loudness",
}


def planned_mastering_plan() -> dict[str, object]:
    checks = []
    for index, category in enumerate(REQUIRED_CATEGORIES, start=1):
        operator, value, units = EXPECTED[category]
        checks.append(
            {
                "check_id": f"LANTERN-U01-QC{index:03d}",
                "category": category,
                "required": True,
                "criterion": {
                    "metric": category,
                    "state": "unresolved" if category in {"audio-true-peak", "audio-loudness"} else "supplied",
                    "operator": operator,
                    "expected_value": value,
                    "units": units,
                    "source_reference": "delivery/LANTERN-specification.md",
                },
                "observed": {
                    "value": None,
                    "units": None,
                    "master_version_id": None,
                    "evidence_ids": [],
                },
                "upstream_references": {
                    "title_item_ids": ["LANTERN-U01-TT001"] if category.startswith(("caption", "title")) else [],
                    "sound_item_ids": ["LANTERN-U01-PS001"] if category.startswith(("audio", "av-sync")) else [],
                    "color_item_ids": ["LANTERN-U01-CL001"] if category in {"video-levels", "color-completion"} else [],
                    "vfx_item_ids": ["LANTERN-U01-FX001"] if category in {"compression-artifacts", "vfx-completion"} else [],
                },
                "result": "planned",
            }
        )
    return {
        "schema_version": "0.3.0",
        "project_id": "LANTERN",
        "unit_id": "LANTERN-U01",
        "source_context": {
            "master_versions": [],
            "current_master_version_id": None,
            "title_items": [{"item_id": "LANTERN-U01-TT001", "source_reference": "post/titles-captions-plan.json#/items/0"}],
            "sound_items": [{"item_id": "LANTERN-U01-PS001", "source_reference": "post/sound-post-plan.json#/items/0"}],
            "color_items": [{"item_id": "LANTERN-U01-CL001", "source_reference": "post/color-plan.json#/items/0"}],
            "vfx_items": [{"item_id": "LANTERN-U01-FX001", "source_reference": "post/vfx-post-plan.json#/items/0"}],
            "evidence": [],
        },
        "checks": checks,
        "deliverables": [
            {
                "deliverable_id": "LANTERN-U01-DL001",
                "kind": "picture-sound-master",
                "required": True,
                "status": "planned",
                "master_version_id": None,
                "source_reference": None,
                "evidence_ids": [],
            },
            {
                "deliverable_id": "LANTERN-U01-DL002",
                "kind": "captions",
                "required": True,
                "status": "planned",
                "master_version_id": None,
                "source_reference": None,
                "evidence_ids": [],
            },
            {
                "deliverable_id": "LANTERN-U01-DL003",
                "kind": "qc-report",
                "required": True,
                "status": "planned",
                "master_version_id": None,
                "source_reference": None,
                "evidence_ids": [],
            },
        ],
        "approval": {
            "state": "pending",
            "master_version_id": None,
            "scope": "delivery-master-and-qc",
            "evidence_ids": [],
        },
        "readiness": {
            "state": "not-ready",
            "required_check_ids": [check["check_id"] for check in checks],
            "required_deliverable_ids": [
                "LANTERN-U01-DL001",
                "LANTERN-U01-DL002",
                "LANTERN-U01-DL003",
            ],
            "rationale": "No master or applicable QC evidence was supplied; every check remains planned.",
        },
        "assumptions": [
            "Stereo means the supplied L,R layout requirement; channel count alone will not establish this layout."
        ],
        "uncertainties": [
            "True-peak, loudness, safe-area, codec, container, and other vendor thresholds remain supplied-specification decisions."
        ],
    }


def _add_master(payload: dict[str, object], version: str = "LANTERN-U01-MV002") -> None:
    context = payload["source_context"]
    assert isinstance(context, dict)
    context["master_versions"] = [
        {
            "master_version_id": version,
            "label": "r2",
            "source_reference": "masters/LANTERN-U01-r2.mov",
            "checksum": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
        }
    ]
    context["current_master_version_id"] = version


def _observe_check(payload: dict[str, object], category: str, value: object, units: str | None = None) -> None:
    checks = payload["checks"]
    context = payload["source_context"]
    assert isinstance(checks, list) and isinstance(context, dict)
    check = next(record for record in checks if record["category"] == category)
    evidence_id = f"LANTERN-QE{len(context['evidence']) + 1:03d}"
    check["observed"] = {
        "value": value,
        "units": units,
        "master_version_id": "LANTERN-U01-MV002",
        "evidence_ids": [evidence_id],
    }
    check["result"] = "pass"
    context["evidence"].append(
        {
            "evidence_id": evidence_id,
            "kind": "measurement" if category in MEASUREMENT_CATEGORIES else "inspection",
            "source_kind": "supplied-measurement-report" if category in MEASUREMENT_CATEGORIES else "supplied-inspection-record",
            "applicability": "applicable",
            "target_check_id": check["check_id"],
            "target_deliverable_id": None,
            "criterion": copy.deepcopy(check["criterion"]),
            "observed_value": value,
            "units": units,
            "master_version_id": "LANTERN-U01-MV002",
            "scope": f"check:{check['check_id']}",
            "source_reference": f"qc/master-r2-report.json#/checks/{check['check_id']}",
        }
    )


def partial_metadata_plan() -> dict[str, object]:
    payload = planned_mastering_plan()
    _add_master(payload)
    for category, value, units in (
        ("video-resolution", "1920x1080", "pixels"),
        ("frame-rate", 24, "fps"),
        ("aspect-ratio", "16:9", "ratio"),
        ("duration", 60, "seconds"),
        ("audio-channel-count", 2, "channels"),
        ("audio-sample-peak", -2, "dBFS"),
    ):
        _observe_check(payload, category, value, units)
    payload["readiness"]["rationale"] = "The supplied metadata verifies six exact r2 fields; required visual, audio-layout, caption, title, artifact, and approval checks remain planned."
    return payload


def ready_mastering_plan() -> dict[str, object]:
    payload = planned_mastering_plan()
    _add_master(payload)
    for category, operator, value, units in (
        ("audio-true-peak", "less-than-or-equal", -1, "dBTP"),
        ("audio-loudness", "equals", -23, "LUFS"),
    ):
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"].update(state="supplied", operator=operator, expected_value=value, units=units)
    for category in REQUIRED_CATEGORIES:
        check = next(record for record in payload["checks"] if record["category"] == category)
        _observe_check(payload, category, check["criterion"]["expected_value"], check["criterion"]["units"])

    context = payload["source_context"]
    deliverables = payload["deliverables"]
    assert isinstance(context, dict) and isinstance(deliverables, list)
    for deliverable in deliverables:
        evidence_id = f"LANTERN-QE{len(context['evidence']) + 1:03d}"
        deliverable.update(
            status="verified",
            master_version_id="LANTERN-U01-MV002",
            source_reference=f"delivery/{deliverable['deliverable_id']}",
            evidence_ids=[evidence_id],
        )
        context["evidence"].append(
            {
                "evidence_id": evidence_id,
                "kind": "deliverable-verification",
                "source_kind": "supplied-deliverable-record",
                "applicability": "applicable",
                "target_check_id": None,
                "target_deliverable_id": deliverable["deliverable_id"],
                "criterion": None,
                "observed_value": "verified",
                "units": None,
                "master_version_id": "LANTERN-U01-MV002",
                "scope": f"deliverable:{deliverable['deliverable_id']}",
                "source_reference": f"qc/deliverable-inventory.json#/{deliverable['deliverable_id']}",
            }
        )
    approval_id = f"LANTERN-QE{len(context['evidence']) + 1:03d}"
    context["evidence"].append(
        {
            "evidence_id": approval_id,
            "kind": "human-approval",
            "source_kind": "supplied-human-decision",
            "applicability": "applicable",
            "target_check_id": None,
            "target_deliverable_id": None,
            "criterion": None,
            "observed_value": "approved",
            "units": None,
            "master_version_id": "LANTERN-U01-MV002",
            "scope": "delivery-master-and-qc",
            "source_reference": "approvals/LANTERN-U01-r2-delivery.json",
        }
    )
    payload["approval"] = {
        "state": "approved",
        "master_version_id": "LANTERN-U01-MV002",
        "scope": "delivery-master-and-qc",
        "evidence_ids": [approval_id],
    }
    payload["readiness"].update(
        state="ready",
        rationale="All required checks and deliverables for the exact r2 master are verified and the same scope is human-approved.",
    )
    return payload


def errors(payload: dict[str, object], repository_root) -> list[str]:
    return validate_artifact("mastering-qc-plan", payload, repository_root)


def test_mastering_qc_accepts_useful_specs_only_plan_without_claiming_pass(repository_root) -> None:
    assert errors(planned_mastering_plan(), repository_root) == []


def test_mastering_qc_accepts_partial_supplied_metadata_but_keeps_not_ready(repository_root) -> None:
    payload = partial_metadata_plan()
    assert payload["readiness"]["state"] == "not-ready"
    assert errors(payload, repository_root) == []


def test_mastering_qc_accepts_fully_evidenced_ready_plan(repository_root) -> None:
    assert errors(ready_mastering_plan(), repository_root) == []


def test_mastering_qc_rejects_wrong_owned_or_duplicate_ids(repository_root) -> None:
    payload = planned_mastering_plan()
    payload["checks"][0]["check_id"] = "OTHER-U01-QC001"
    payload["checks"][1]["check_id"] = "OTHER-U01-QC001"
    result = errors(payload, repository_root)
    assert any("must match LANTERN-U01-QC###" in error for error in result)
    assert any("duplicate QC check ID" in error for error in result)


def test_mastering_qc_rejects_pass_or_fail_without_applicable_evidence(repository_root) -> None:
    for result_name in ("pass", "fail"):
        payload = partial_metadata_plan()
        check = next(record for record in payload["checks"] if record["category"] == "av-sync")
        check["result"] = result_name
        check["observed"] = {
            "value": "synchronous",
            "units": None,
            "master_version_id": "LANTERN-U01-MV002",
            "evidence_ids": [],
        }
        assert any("pass/fail requires applicable current-master evidence" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_numeric_observation_without_source(repository_root) -> None:
    payload = partial_metadata_plan()
    evidence = payload["source_context"]["evidence"][1]
    evidence["source_reference"] = ""
    result = errors(payload, repository_root)
    assert any("source_reference" in error for error in result)


def test_mastering_qc_rejects_unknown_title_sound_color_and_vfx_references(repository_root) -> None:
    payload = planned_mastering_plan()
    check = payload["checks"][0]
    check["upstream_references"] = {
        "title_item_ids": ["LANTERN-U01-TT999"],
        "sound_item_ids": ["LANTERN-U01-PS999"],
        "color_item_ids": ["LANTERN-U01-CL999"],
        "vfx_item_ids": ["LANTERN-U01-FX999"],
    }
    result = errors(payload, repository_root)
    for label in ("title", "sound", "color", "VFX"):
        assert any(f"unknown {label} item" in error for error in result)


def test_mastering_qc_rejects_evidence_for_wrong_check_criterion_version_value_or_units(repository_root) -> None:
    mutations = (
        ("target_check_id", "LANTERN-U01-QC024"),
        ("criterion", {"metric": "duration", "state": "supplied", "operator": "equals", "expected_value": 60, "units": "seconds", "source_reference": "delivery/LANTERN-specification.md"}),
        ("master_version_id", "LANTERN-U01-MV001"),
        ("observed_value", 25),
        ("units", "frames-per-second"),
    )
    for field, value in mutations:
        payload = partial_metadata_plan()
        evidence = payload["source_context"]["evidence"][1]
        evidence[field] = value
        result = errors(payload, repository_root)
        assert any("exact check, criterion, observed value, units, and current master version" in error for error in result), (field, result)


def test_mastering_qc_rejects_machine_comparison_that_disagrees_with_result(repository_root) -> None:
    for result_name, observed in (("pass", 25), ("fail", 24)):
        payload = partial_metadata_plan()
        check = next(record for record in payload["checks"] if record["category"] == "frame-rate")
        check["result"] = result_name
        check["observed"]["value"] = observed
        evidence_id = check["observed"]["evidence_ids"][0]
        evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
        evidence["observed_value"] = observed
        assert any("disagrees with the machine-comparable criterion" in error for error in errors(payload, repository_root))


def test_mastering_qc_does_not_reuse_sample_peak_as_true_peak_or_channel_count_as_layout(repository_root) -> None:
    for target_category, source_category in (("audio-true-peak", "audio-sample-peak"), ("audio-channel-layout", "audio-channel-count")):
        payload = partial_metadata_plan()
        source = next(record for record in payload["checks"] if record["category"] == source_category)
        target = next(record for record in payload["checks"] if record["category"] == target_category)
        target["result"] = "pass"
        target["observed"] = copy.deepcopy(source["observed"])
        assert any("exact check, criterion, observed value, units, and current master version" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_ready_when_required_checks_are_not_passed(repository_root) -> None:
    for blocked_result in ("planned", "fail", "human-review"):
        payload = ready_mastering_plan()
        payload["checks"][0]["result"] = blocked_result
        payload["readiness"]["state"] = "ready"
        result = errors(payload, repository_root)
        assert any("required checks must all pass before readiness" in error for error in result), blocked_result


def test_mastering_qc_rejects_deleting_required_coverage_or_hiding_it_from_readiness(repository_root) -> None:
    payload = planned_mastering_plan()
    missing = payload["checks"].pop()
    payload["readiness"]["required_check_ids"].remove(missing["check_id"])
    result = errors(payload, repository_root)
    assert any("required QC category" in error for error in result)

    payload = planned_mastering_plan()
    payload["readiness"]["required_check_ids"].pop()
    assert any("must equal all required QC check IDs" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_ready_with_unverified_required_deliverable(repository_root) -> None:
    payload = ready_mastering_plan()
    payload["deliverables"][0]["status"] = "present"
    assert any("required deliverables must all be verified before readiness" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_approval_from_another_version_or_scope(repository_root) -> None:
    for field, value in (("master_version_id", "LANTERN-U01-MV001"), ("scope", "picture-only")):
        payload = ready_mastering_plan()
        payload["source_context"]["master_versions"].append(
            {
                "master_version_id": "LANTERN-U01-MV001",
                "label": "r1",
                "source_reference": "masters/LANTERN-U01-r1.mov",
                "checksum": None,
            }
        )
        evidence_id = payload["approval"]["evidence_ids"][0]
        evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
        evidence[field] = value
        result = errors(payload, repository_root)
        assert any("approval evidence must bind the exact current master version and review scope" in error for error in result), (field, result)


def test_mastering_qc_validates_unused_historical_evidence_internally(repository_root) -> None:
    payload = partial_metadata_plan()
    payload["source_context"]["evidence"].append(
        {
            "evidence_id": "LANTERN-QE999",
            "kind": "measurement",
            "source_kind": "supplied-measurement-report",
            "applicability": "applicable",
            "target_check_id": "LANTERN-U01-QC999",
            "target_deliverable_id": None,
            "criterion": copy.deepcopy(payload["checks"][0]["criterion"]),
            "observed_value": "1920x1080",
            "units": "pixels",
            "master_version_id": "LANTERN-U01-MV001",
            "scope": "check:LANTERN-U01-QC999",
            "source_reference": "qc/master-r1-report.json",
        }
    )
    result = errors(payload, repository_root)
    assert any("unknown QC check" in error for error in result)
    assert any("unknown master version" in error for error in result)


def test_mastering_qc_rejects_unused_evidence_with_mismatched_target_contract(repository_root) -> None:
    payload = partial_metadata_plan()
    payload["source_context"]["evidence"].append(
        {
            "evidence_id": "LANTERN-QE999",
            "kind": "measurement",
            "source_kind": "supplied-measurement-report",
            "applicability": "historical",
            "target_check_id": "LANTERN-U01-QC001",
            "target_deliverable_id": None,
            "criterion": copy.deepcopy(payload["checks"][3]["criterion"]),
            "observed_value": 60,
            "units": "seconds",
            "master_version_id": "LANTERN-U01-MV002",
            "scope": "check:LANTERN-U01-QC001",
            "source_reference": "qc/unused-report.json",
        }
    )
    assert any("evidence criterion and scope must match its target QC check" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_ready_after_required_master_or_qc_report_is_deleted(repository_root) -> None:
    for kind in ("picture-sound-master", "qc-report"):
        payload = ready_mastering_plan()
        deliverable = next(record for record in payload["deliverables"] if record["kind"] == kind)
        payload["deliverables"].remove(deliverable)
        payload["readiness"]["required_deliverable_ids"].remove(deliverable["deliverable_id"])
        assert any("missing required deliverable kind" in error for error in errors(payload, repository_root)), kind


def test_mastering_qc_rejects_ready_with_narrow_picture_only_approval_scope(repository_root) -> None:
    payload = ready_mastering_plan()
    payload["approval"]["scope"] = "picture-only"
    evidence_id = payload["approval"]["evidence_ids"][0]
    evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
    evidence["scope"] = "picture-only"

    assert any("approved readiness scope must be delivery-master-and-qc" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_pass_when_observed_units_disagree_with_criterion(repository_root) -> None:
    payload = partial_metadata_plan()
    check = next(record for record in payload["checks"] if record["category"] == "frame-rate")
    evidence_id = check["observed"]["evidence_ids"][0]
    evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
    check["observed"]["units"] = "frames-per-second"
    evidence["units"] = "frames-per-second"

    assert any("observed units must equal criterion units" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_unbound_applicable_evidence_and_noncurrent_applicability(repository_root) -> None:
    for version, expected in (
        ("LANTERN-U01-MV002", "applicable check evidence must be bound to the target observation"),
        ("LANTERN-U01-MV001", "applicable evidence must use the current master version"),
    ):
        payload = partial_metadata_plan()
        payload["source_context"]["master_versions"].append(
            {
                "master_version_id": "LANTERN-U01-MV001",
                "label": "r1",
                "source_reference": "masters/LANTERN-U01-r1.mov",
                "checksum": None,
            }
        )
        check = payload["checks"][0]
        payload["source_context"]["evidence"].append(
            {
                "evidence_id": "LANTERN-QE999",
                "kind": "measurement",
                "source_kind": "supplied-measurement-report",
                "applicability": "applicable",
                "target_check_id": check["check_id"],
                "target_deliverable_id": None,
                "criterion": copy.deepcopy(check["criterion"]),
                "observed_value": "1280x720",
                "units": "pixels",
                "master_version_id": version,
                "scope": f"check:{check['check_id']}",
                "source_reference": "qc/second-report.json",
            }
        )

        assert any(expected in error for error in errors(payload, repository_root)), (version, errors(payload, repository_root))


def test_mastering_qc_accepts_explicitly_historical_evidence_for_known_old_version(repository_root) -> None:
    payload = partial_metadata_plan()
    payload["source_context"]["master_versions"].append(
        {
            "master_version_id": "LANTERN-U01-MV001",
            "label": "r1",
            "source_reference": "masters/LANTERN-U01-r1.mov",
            "checksum": None,
        }
    )
    check = payload["checks"][0]
    payload["source_context"]["evidence"].append(
        {
            "evidence_id": "LANTERN-QE999",
            "kind": "measurement",
            "source_kind": "supplied-measurement-report",
            "applicability": "historical",
            "target_check_id": check["check_id"],
            "target_deliverable_id": None,
            "criterion": copy.deepcopy(check["criterion"]),
            "observed_value": "1280x720",
            "units": "pixels",
            "master_version_id": "LANTERN-U01-MV001",
            "scope": f"check:{check['check_id']}",
            "source_reference": "qc/master-r1-report.json",
        }
    )

    assert errors(payload, repository_root) == []


def test_mastering_qc_rejects_pass_for_unresolved_placeholder_review_criteria(repository_root) -> None:
    payload = partial_metadata_plan()
    check = next(record for record in payload["checks"] if record["category"] == "audio-true-peak")
    assert check["criterion"]["operator"] == "review"
    assert check["criterion"]["expected_value"] == "Supply the delivery threshold"
    _observe_check(payload, "audio-true-peak", -1, "dBTP")

    assert any("unresolved criterion cannot pass or fail" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_master_filename_as_measurement_or_inspection_evidence(repository_root) -> None:
    payload = partial_metadata_plan()
    master_reference = payload["source_context"]["master_versions"][0]["source_reference"]
    payload["source_context"]["evidence"][0]["source_reference"] = master_reference

    assert any("master filename or source is not QC evidence" in error for error in errors(payload, repository_root))


def _add_structured_source_kinds(payload: dict[str, object]) -> None:
    source_kinds = {
        "measurement": "supplied-measurement-report",
        "inspection": "supplied-inspection-record",
        "deliverable-verification": "supplied-deliverable-record",
        "human-approval": "supplied-human-decision",
    }
    for evidence in payload["source_context"]["evidence"]:
        evidence["source_kind"] = source_kinds[evidence["kind"]]


def test_mastering_qc_accepts_structured_evidence_source_kinds(repository_root) -> None:
    payload = partial_metadata_plan()
    _add_structured_source_kinds(payload)

    assert errors(payload, repository_root) == []


def test_mastering_qc_rejects_mismatched_or_filename_only_source_kind(repository_root) -> None:
    for source_kind, expected in (
        ("supplied-inspection-record", "source_kind must be supplied-measurement-report for measurement evidence"),
        ("master-filename-only", "source_kind"),
    ):
        payload = partial_metadata_plan()
        _add_structured_source_kinds(payload)
        payload["source_context"]["evidence"][0]["source_kind"] = source_kind
        assert any(expected in error for error in errors(payload, repository_root)), (source_kind, errors(payload, repository_root))


def test_mastering_qc_rejects_historical_evidence_with_internally_mismatched_units(repository_root) -> None:
    payload = partial_metadata_plan()
    payload["source_context"]["master_versions"].append(
        {
            "master_version_id": "LANTERN-U01-MV001",
            "label": "r1",
            "source_reference": "masters/LANTERN-U01-r1.mov",
            "checksum": None,
        }
    )
    check = payload["checks"][0]
    criterion = copy.deepcopy(check["criterion"])
    criterion["units"] = "seconds"
    payload["source_context"]["evidence"].append(
        {
            "evidence_id": "LANTERN-QE999",
            "kind": "measurement",
            "source_kind": "supplied-measurement-report",
            "applicability": "historical",
            "target_check_id": check["check_id"],
            "target_deliverable_id": None,
            "criterion": criterion,
            "observed_value": "1280x720",
            "units": "pixels",
            "master_version_id": "LANTERN-U01-MV001",
            "scope": f"check:{check['check_id']}",
            "source_reference": "qc/master-r1-report.json",
        }
    )

    assert any("evidence criterion units must match its observed units" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_measurable_pass_with_review_operator_even_if_marked_supplied(repository_root) -> None:
    payload = partial_metadata_plan()
    check = next(record for record in payload["checks"] if record["category"] == "audio-sample-peak")
    check["criterion"].update(state="supplied", operator="review", expected_value="Supply the delivery threshold")
    evidence_id = check["observed"]["evidence_ids"][0]
    evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
    evidence["criterion"] = copy.deepcopy(check["criterion"])

    assert any("measurable supplied criterion must use a machine-comparable operator" in error for error in errors(payload, repository_root))


def _plan_with_unbound_historical_delivery_and_approval_evidence() -> dict[str, object]:
    payload = partial_metadata_plan()
    payload["source_context"]["evidence"].extend(
        [
            {
                "evidence_id": "LANTERN-QE900",
                "kind": "deliverable-verification",
                "source_kind": "supplied-deliverable-record",
                "applicability": "historical",
                "target_check_id": None,
                "target_deliverable_id": "LANTERN-U01-DL001",
                "criterion": None,
                "observed_value": "verified",
                "units": None,
                "master_version_id": "LANTERN-U01-MV002",
                "scope": "deliverable:LANTERN-U01-DL001",
                "source_reference": "qc/historical-deliverable-record.json",
            },
            {
                "evidence_id": "LANTERN-QE901",
                "kind": "human-approval",
                "source_kind": "supplied-human-decision",
                "applicability": "superseded",
                "target_check_id": None,
                "target_deliverable_id": None,
                "criterion": None,
                "observed_value": "approved",
                "units": None,
                "master_version_id": "LANTERN-U01-MV002",
                "scope": "picture-only",
                "source_reference": "approvals/superseded-picture-review.json",
            },
        ]
    )
    return payload


def test_mastering_qc_accepts_internally_consistent_unbound_historical_delivery_and_approval_evidence(repository_root) -> None:
    assert errors(_plan_with_unbound_historical_delivery_and_approval_evidence(), repository_root) == []


def test_mastering_qc_rejects_internally_malformed_historical_deliverable_evidence(repository_root) -> None:
    for field, value in (
        ("scope", "deliverable:LANTERN-U01-DL002"),
        ("observed_value", "present"),
        ("units", "files"),
    ):
        payload = _plan_with_unbound_historical_delivery_and_approval_evidence()
        payload["source_context"]["evidence"][-2][field] = value
        result = errors(payload, repository_root)
        assert any("deliverable evidence must be internally consistent" in error for error in result), (field, result)


def test_mastering_qc_rejects_internally_malformed_historical_approval_evidence(repository_root) -> None:
    for field, value, expected in (
        ("observed_value", "pending", "approval evidence must be internally consistent"),
        ("units", "decision", "approval evidence must be internally consistent"),
        ("scope", "", "scope"),
    ):
        payload = _plan_with_unbound_historical_delivery_and_approval_evidence()
        payload["source_context"]["evidence"][-1][field] = value
        result = errors(payload, repository_root)
        assert any(expected in error for error in result), (field, result)


def test_mastering_qc_normalizes_master_paths_before_rejecting_filename_evidence(repository_root) -> None:
    for disguised_reference in (
        "masters/LANTERN-U01-r2.mov#metadata",
        "masters/LANTERN-U01-r2.mov?report=1",
        "./masters/LANTERN-U01-r2.mov",
        "masters/temp/../LANTERN-U01-r2.mov",
    ):
        payload = partial_metadata_plan()
        payload["source_context"]["evidence"][0]["source_reference"] = disguised_reference
        result = errors(payload, repository_root)
        assert any("master filename or source is not QC evidence" in error for error in result), (disguised_reference, result)


def test_mastering_qc_rejects_wrong_value_types_and_nonfinite_numeric_measurements(repository_root) -> None:
    cases = (
        ("frame-rate", "expected", "24"),
        ("duration", "expected", True),
        ("audio-channel-count", "observed", "2"),
        ("audio-sample-peak", "observed", float("nan")),
        ("video-resolution", "expected", 1920),
        ("aspect-ratio", "observed", 1.777),
        ("audio-channel-layout", "observed", 2),
        ("captions-presence", "expected", "true"),
        ("missing-frames", "observed", 0),
    )
    for category, side, value in cases:
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        if side == "expected":
            check["criterion"]["expected_value"] = value
            for evidence_id in check["observed"]["evidence_ids"]:
                evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
                evidence["criterion"] = copy.deepcopy(check["criterion"])
        else:
            check["observed"]["value"] = value
            for evidence_id in check["observed"]["evidence_ids"]:
                evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
                evidence["observed_value"] = value
        result = errors(payload, repository_root)
        assert any("value type" in error or "finite number" in error for error in result), (category, side, value, result)


def test_mastering_qc_rejects_oversized_numeric_measurement_without_crashing(repository_root) -> None:
    payload = ready_mastering_plan()
    check = next(record for record in payload["checks"] if record["category"] == "audio-sample-peak")
    oversized = 10**1000
    check["observed"]["value"] = oversized
    evidence_id = check["observed"]["evidence_ids"][0]
    evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
    evidence["observed_value"] = oversized

    result = errors(payload, repository_root)
    assert any("finite number" in error for error in result)


def test_mastering_qc_never_silently_skips_invalid_machine_comparison(repository_root) -> None:
    payload = partial_metadata_plan()
    check = next(record for record in payload["checks"] if record["category"] == "frame-rate")
    check["observed"]["value"] = "twenty-four"
    evidence_id = check["observed"]["evidence_ids"][0]
    evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
    evidence["observed_value"] = "twenty-four"

    assert any("machine-comparable criterion has incompatible operands" in error for error in errors(payload, repository_root))


def test_mastering_qc_rejects_verified_qc_report_that_is_the_master_file(repository_root) -> None:
    for disguised_reference in (
        "masters/LANTERN-U01-r2.mov",
        "masters/LANTERN-U01-r2.mov#qc-report",
        "./masters/LANTERN-U01-r2.mov?report=1",
    ):
        payload = ready_mastering_plan()
        report = next(record for record in payload["deliverables"] if record["kind"] == "qc-report")
        report["source_reference"] = disguised_reference
        result = errors(payload, repository_root)
        assert any("QC report must be distinct from the current master source" in error for error in result), (disguised_reference, result)


def test_mastering_qc_rejects_empty_resolution_aspect_ratio_and_channel_layout(repository_root) -> None:
    for category in ("video-resolution", "aspect-ratio", "audio-channel-layout"):
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"]["expected_value"] = ""
        check["observed"]["value"] = ""
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = ""

        result = errors(payload, repository_root)
        assert any("must be a non-empty string" in error for error in result), (category, result)


def test_mastering_qc_rejects_nonpositive_frame_rate_and_duration(repository_root) -> None:
    for category, invalid_value in (("frame-rate", 0), ("frame-rate", -24), ("duration", 0), ("duration", -60)):
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"]["expected_value"] = invalid_value
        check["observed"]["value"] = invalid_value
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = invalid_value

        result = errors(payload, repository_root)
        assert any("must be greater than zero" in error for error in result), (category, invalid_value, result)


def test_mastering_qc_rejects_fractional_or_nonpositive_channel_count(repository_root) -> None:
    for invalid_value in (2.5, 0, -1):
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == "audio-channel-count")
        check["criterion"]["expected_value"] = invalid_value
        check["observed"]["value"] = invalid_value
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = invalid_value

        result = errors(payload, repository_root)
        assert any("must be a positive integer" in error for error in result), (invalid_value, result)


def test_mastering_qc_rejects_captions_and_titles_presence_with_equals(repository_root) -> None:
    for category in ("captions-presence", "titles-presence"):
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"]["operator"] = "equals"
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])

        result = errors(payload, repository_root)
        assert any("presence check must use present or absent" in error for error in result), (category, result)


def test_mastering_qc_rejects_string_captions_and_titles_presence_values(repository_root) -> None:
    for category in ("captions-presence", "titles-presence"):
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"]["expected_value"] = "present"
        check["observed"]["value"] = "present"
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = "present"

        result = errors(payload, repository_root)
        assert any("presence value type must be boolean" in error for error in result), (category, result)


def test_mastering_qc_rejects_contradictory_presence_operator_semantics(repository_root) -> None:
    cases = (
        ("captions-presence", "present", False),
        ("captions-presence", "absent", True),
        ("titles-presence", "present", False),
        ("titles-presence", "absent", True),
        ("missing-frames", "absent", True),
    )
    for category, operator, value in cases:
        payload = ready_mastering_plan()
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"].update(operator=operator, expected_value=value)
        check["observed"]["value"] = value
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = value

        result = errors(payload, repository_root)
        assert any("disagrees with the machine-comparable criterion" in error for error in result), (category, operator, value, result)


def test_mastering_qc_rejects_presence_operator_with_contradictory_expected_value(repository_root) -> None:
    cases = (
        ("captions-presence", "present", False),
        ("captions-presence", "absent", True),
        ("titles-presence", "present", False),
        ("titles-presence", "absent", True),
        ("missing-frames", "absent", True),
    )
    for category, operator, value in cases:
        payload = ready_mastering_plan()
        payload["readiness"]["state"] = "not-ready"
        check = next(record for record in payload["checks"] if record["category"] == category)
        check["criterion"].update(operator=operator, expected_value=value)
        check["observed"]["value"] = value
        check["result"] = "planned"
        for evidence_id in check["observed"]["evidence_ids"]:
            evidence = next(record for record in payload["source_context"]["evidence"] if record["evidence_id"] == evidence_id)
            evidence["criterion"] = copy.deepcopy(check["criterion"])
            evidence["observed_value"] = value

        result = errors(payload, repository_root)
        assert any(f"presence operator {operator} requires expected_value" in error for error in result), (category, operator, value, result)
