from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifacts import validate_artifact_file
from .package import resolve_scene_package_profile, validate_scene_package
from .project_contracts import PROJECT_FORMATS, PRODUCTION_MODES, PRODUCTION_PROFILE, STORY_PROFILE
from .production_package import derive_production_index_at, validate_production_package
from .post_package import POST_PROFILE, validate_post_package
from .reporting import render_validation_report
from .story_package import validate_story_package
from .project_package import validate_project
from .validator import validate_repository


def _add_output_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json"), default="text")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m cine_skills")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate a skills repository")
    validate.add_argument("root", nargs="?", default=".")
    _add_output_format(validate)
    validate_artifact = subparsers.add_parser(
        "validate-artifact", help="validate an artifact JSON file"
    )
    validate_artifact.add_argument("schema_name")
    validate_artifact.add_argument("json_file")
    validate_artifact.add_argument("--root", default=".")
    _add_output_format(validate_artifact)
    validate_package = subparsers.add_parser(
        "validate-package", help="validate a complete scene package"
    )
    validate_package.add_argument("package_dir")
    validate_package.add_argument("--root", default=".")
    validate_package.add_argument(
        "--profile",
        choices=("auto", "core-v0.1", "full-v1"),
        default="auto",
    )
    _add_output_format(validate_package)
    validate_story = subparsers.add_parser(
        "validate-story", help="validate a v2 story package"
    )
    validate_story.add_argument("story_dir")
    validate_story.add_argument(
        "--project-format", choices=PROJECT_FORMATS, required=True
    )
    _add_output_format(validate_story)
    validate_production = subparsers.add_parser(
        "validate-production", help="validate a v2 production package"
    )
    validate_production.add_argument("package_dir")
    validate_production.add_argument("--root", default=".")
    validate_production.add_argument(
        "--production-mode", choices=PRODUCTION_MODES, action="append", required=True
    )
    validate_production.add_argument(
        "--allow-nested",
        action="store_true",
        help="allow a manifest-selected production directory nested under a project",
    )
    _add_output_format(validate_production)
    validate_post = subparsers.add_parser("validate-post", help="validate a v2 post package")
    validate_post.add_argument("package_dir")
    validate_post.add_argument("--root", default=".")
    _add_output_format(validate_post)
    validate_project_parser = subparsers.add_parser("validate-project", help="validate a complete v2 creative project")
    validate_project_parser.add_argument("project_dir")
    validate_project_parser.add_argument("--root", default=".")
    validate_project_parser.add_argument("--profile", default="full-creative-v2", choices=("full-creative-v2",))
    _add_output_format(validate_project_parser)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        errors = validate_repository(Path(args.root))
        print(render_validation_report(args.command, errors, args.format))
        return 1 if errors else 0
    if args.command == "validate-artifact":
        errors = validate_artifact_file(
            args.schema_name, Path(args.json_file), Path(args.root)
        )
        print(render_validation_report(args.command, errors, args.format))
        return 1 if errors else 0
    if args.command == "validate-package":
        resolved_profile = resolve_scene_package_profile(
            Path(args.package_dir), args.profile
        )
        errors = validate_scene_package(
            Path(args.package_dir), Path(args.root), resolved_profile
        )
        print(
            render_validation_report(
                args.command, errors, args.format, resolved_profile
            )
        )
        return 1 if errors else 0
    if args.command == "validate-story":
        errors = validate_story_package(
            Path(args.story_dir), Path("."), args.project_format
        )
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "command": args.command,
                        "errors": sorted(errors),
                        "profile": STORY_PROFILE,
                        "valid": not errors,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
        elif errors:
            print(render_validation_report(args.command, errors, args.format))
        else:
            print("Story package validation passed.")
        return 1 if errors else 0
    if args.command == "validate-production":
        package = Path(args.package_dir)
        root = Path(args.root)
        upstream, errors = derive_production_index_at(
            package, root, args.production_mode
        )
        if upstream is not None:
            errors.extend(
                validate_production_package(
                    package,
                    root,
                    args.production_mode,
                    upstream,
                    enforce_directory_name=not args.allow_nested,
                )
            )
        errors = sorted(set(errors))
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "command": args.command,
                        "errors": errors,
                        "profile": PRODUCTION_PROFILE,
                        "valid": not errors,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
        elif errors:
            print(render_validation_report(args.command, errors, args.format))
        else:
            print("Production package validation passed.")
        return 1 if errors else 0
    if args.command == "validate-post":
        package = Path(args.package_dir)
        root = Path(args.root)
        # CLI derivation is intentionally limited to the package's declared edit context.
        from .project_validation import load_validated_artifacts
        from .project_contracts import required_post_artifacts, ProjectIndex
        payloads, errors = load_validated_artifacts(package, required_post_artifacts(), root)
        edit = payloads.get("edit-plan.json", {})
        context = edit.get("source_context", {}) if isinstance(edit, dict) else {}
        segments = edit.get("segments", []) if isinstance(edit, dict) else []
        segment_ids = {
            item.get("segment_id") for item in segments
            if isinstance(item, dict) and isinstance(item.get("segment_id"), str)
        }
        if isinstance(context, dict):
            segment_ids |= {
                item.get("segment_id") for item in context.get("edit_segments", [])
                if isinstance(item, dict) and isinstance(item.get("segment_id"), str)
            }
        shot_ids = {
            item.get("shot_id") for item in context.get("shots", [])
            if isinstance(item, dict) and isinstance(item.get("shot_id"), str)
        } if isinstance(context, dict) else set()
        media_ids = {
            item.get("media_id") for item in context.get("media_items", [])
            if isinstance(item, dict) and isinstance(item.get("media_id"), str)
        } if isinstance(context, dict) else set()
        project_id = edit.get("project_id", "") if isinstance(edit, dict) else ""
        unit_id = edit.get("unit_id") if isinstance(edit, dict) else None
        upstream = ProjectIndex(
            project_id=project_id,
            project_format=edit.get("project_format", "") if isinstance(edit, dict) else "",
            production_modes=(),
            unit_ids=frozenset({unit_id}) if isinstance(unit_id, str) else frozenset(),
            shot_ids=frozenset(shot_ids),
            media_ids=frozenset(media_ids),
            edit_segment_ids=frozenset(segment_ids),
        )
        errors.extend(validate_post_package(package, root, upstream))
        errors = sorted(set(errors))
        if args.format == "json":
            print(json.dumps({"command": args.command, "errors": errors, "profile": POST_PROFILE, "valid": not errors}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        elif errors:
            print(render_validation_report(args.command, errors, args.format))
        else:
            print("Post package validation passed.")
        return 1 if errors else 0
    if args.command == "validate-project":
        errors = validate_project(Path(args.project_dir), Path(args.root), args.profile)
        payload = {"command": args.command, "errors": sorted(errors), "profile": args.profile, "valid": not errors}
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        elif errors:
            print(render_validation_report(args.command, errors, args.format, args.profile))
        else:
            print("Project validation passed.")
        return 1 if errors else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
