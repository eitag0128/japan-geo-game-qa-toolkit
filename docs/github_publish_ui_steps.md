# GitHub Publish UI Steps

Use these steps if GitHub CLI is not installed.

1. Open https://github.com/new
2. Repository name: `japan-geo-game-qa-toolkit`
3. Visibility: Public
4. Do not add README, .gitignore, or license in the GitHub UI. This local repository already has them.
5. Create repository.
6. Copy the repository URL, for example:

```text
https://github.com/<your-github-user-or-org>/japan-geo-game-qa-toolkit.git
```

7. From this folder, run:

```powershell
.\scripts\publish_after_repo_created.ps1 -RepositoryUrl "https://github.com/<your-github-user-or-org>/japan-geo-game-qa-toolkit.git"
```

8. Confirm GitHub Actions passes.
9. Replace the placeholder GitHub URL in `docs/openai_codex_for_oss_application_draft.md`.
10. Submit the OpenAI Codex for Open Source form.
