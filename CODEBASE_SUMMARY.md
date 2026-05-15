# Codebase summary

Date: 2026-05-15

Repository: https://github.com/ABOGO-tech237/SGEP

Branches
- `main`: deliberately empty (root kept minimal). Commit: empty root commit.
- `backenddevellopement-01`: active development branch containing the full backend code under the `backend/` folder.

Structure (workspace root)
- `backend/` — Django backend application (apps such as `accounts`, `students`, `teachers`, etc.). All existing source files were moved here.
- `frontend/` — intentionally empty; contains `.gitkeep` as placeholder.

Actions performed
- Moved all project sources into `backend/` and added `frontend/.gitkeep`.
- Created an orphan empty `main` branch to keep the main branch minimal.
- Created/updated `backenddevellopement-01` from the development commit and pushed it to origin.
- Deleted the local `develop` branch (development work continues on `backenddevellopement-01`).

How to get the code locally
```bash
git clone https://github.com/ABOGO-tech237/SGEP.git
git checkout backenddevellopement-01
ls backend
```

Notes / Next steps
- Keep feature/dev branches (e.g., `backenddevellopement-01`) for active work and leave `main` for stable/releases or keep it empty per the chosen workflow.
- If you want, I can remove the remote `develop` branch as well, or create additional dev branches.