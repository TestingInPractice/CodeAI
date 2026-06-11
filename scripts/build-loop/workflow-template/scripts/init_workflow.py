import json, os, sys, shutil, hashlib
from pathlib import Path

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..")

DEFAULT_TRANSITIONS = """
# Transition rules for CodeAI Build Loop
# Project can edit this file to customize allowed transitions

transitions:
  - from: plan-release
    to: implement-spec-stage
  - from: implement-spec-stage
    to: write-tests
  - from: write-tests
    to: integrate-release
  - from: integrate-release
    to: deploy-release
  - from: apply-small-fix
    to: integrate-release
  - from: integrate-release
    to: apply-small-fix
  - from: deploy-release
    to: plan-release
  - from: any
    to: plan-release

phases:
  - id: plan-release
    entry: []
    exit:
      - "judge: passed"
      - "questions: 0"
    allow_backward: true
    allow_restart: true

  - id: implement-spec-stage
    entry:
      - "judge: passed"
    exit:
      - "judge: passed"
      - "tasks: all_completed"
    allow_backward: false
    allow_restart: false

  - id: write-tests
    entry: []
    exit:
      - "judge: passed"
    allow_backward: true
    allow_restart: true

  - id: integrate-release
    entry: []
    exit: []
    allow_backward: false
    allow_restart: false

  - id: deploy-release
    entry: []
    exit: []
    allow_backward: false
    allow_restart: false

  - id: apply-small-fix
    entry: []
    exit: []
    allow_backward: false
    allow_restart: true
"""


def file_checksum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_template(src, dst, checksums):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        return
    shutil.copy2(src, dst)
    checksums[os.path.relpath(dst, os.path.dirname(dst))] = file_checksum(dst)


def init_project(project_dir, force=False, update=False):
    workflow_dir = os.path.join(project_dir, ".workflow")
    existing = os.path.exists(workflow_dir)

    if existing and not force and not update:
        print(f".workflow/ already exists in {project_dir}")
        print("Use --force to overwrite or --update to merge changes")
        sys.exit(1)

    checksums = {}

    def is_template_file(rel):
        """Skip state/spec/task templates — they deploy to different paths"""
        return rel in ("states/initial.json", "states/phase-template.json",
                       "templates/specs/requirements.md", "templates/tasks/task.md")

    def deploy_spec_template(project_dir):
        spec_dir = os.path.join(project_dir, "docs", "specs")
        spec_path = os.path.join(spec_dir, "requirements.md")
        src = os.path.join(TEMPLATE_DIR, "templates", "specs", "requirements.md")
        if not os.path.exists(spec_path):
            os.makedirs(spec_dir, exist_ok=True)
            shutil.copy2(src, spec_path)
            print(f"  created: docs/specs/requirements.md")
            return True
        return False

    def deploy_task_template(project_dir):
        tasks_dir = os.path.join(project_dir, ".workflow", "templates")
        task_path = os.path.join(tasks_dir, "task.md")
        src = os.path.join(TEMPLATE_DIR, "templates", "tasks", "task.md")
        if not os.path.exists(task_path):
            os.makedirs(tasks_dir, exist_ok=True)
            shutil.copy2(src, task_path)
            print(f"  created: .workflow/templates/task.md")
            return True
        return False

    def deploy_state_files(workflow_dir, checksums):
        src_state = os.path.join(TEMPLATE_DIR, "states", "initial.json")
        src_phases = os.path.join(TEMPLATE_DIR, "states", "phase-template.json")
        dst_state = os.path.join(workflow_dir, "state.json")
        dst_phases = os.path.join(workflow_dir, "phases.json")

        for src, dst, key in [(src_state, dst_state, "state.json"),
                               (src_phases, dst_phases, "phases.json")]:
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                checksums[key] = file_checksum(dst)
                print(f"  created: {key}")

    if update and existing:
        old_checksums_path = os.path.join(workflow_dir, ".checksums.json")
        old_checksums = {}
        if os.path.exists(old_checksums_path):
            with open(old_checksums_path) as f:
                old_checksums = json.load(f)

        for root, dirs, files in os.walk(TEMPLATE_DIR):
            for fname in files:
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, TEMPLATE_DIR)
                if is_template_file(rel):
                    continue
                dst = os.path.join(workflow_dir, rel)

                if rel in old_checksums:
                    if os.path.exists(dst):
                        current_chk = file_checksum(dst)
                        if current_chk == old_checksums[rel]:
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            checksums[rel] = file_checksum(dst)
                            print(f"  updated: {rel}")
                        else:
                            checksums[rel] = old_checksums[rel]
                            print(f"  skipped (modified): {rel}")
                    else:
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                        checksums[rel] = file_checksum(dst)
                        print(f"  created: {rel}")
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    checksums[rel] = file_checksum(dst)
                    print(f"  created: {rel}")
        deploy_state_files(workflow_dir, checksums)
    else:
        for root, dirs, files in os.walk(TEMPLATE_DIR):
            for fname in files:
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, TEMPLATE_DIR)
                if is_template_file(rel):
                    continue
                dst = os.path.join(workflow_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                checksums[rel] = file_checksum(dst)

        config_path = os.path.join(workflow_dir, "config.yaml")
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                f.write(DEFAULT_TRANSITIONS)
            checksums["config.yaml"] = file_checksum(config_path)

        deploy_state_files(workflow_dir, checksums)

    deploy_spec_template(project_dir)
    deploy_task_template(project_dir)

    # Write checksums
    checksums_path = os.path.join(workflow_dir, ".checksums.json")
    with open(checksums_path, "w") as f:
        json.dump(checksums, f, indent=2)

    print(f"\n✅ Workflow initialized in {workflow_dir}")
    return workflow_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialize CodeAI Build Loop workflow")
    parser.add_argument("--project", required=True, help="Project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing .workflow/")
    parser.add_argument("--update", action="store_true", help="Update template files (preserves project changes)")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project)
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir, exist_ok=True)

    init_project(project_dir, force=args.force, update=args.update)
