<!-- ITO:START -->

# Apply Guidance

This file is for optional, user-authored guidance specific to `ito agent instruction apply`.

- Ito may update this header block over time.
- Add your apply guidance below the `<!-- ITO:END -->` marker.

<!-- ITO:END -->

## Your Apply Guidance

- After applying changes, run `make check` and `make test` to verify the change is correct and doesn't cause any issues.
- Follow pep8
- use ruff to check for linting issues and fix them before committing.
- use basedpyright to ensure type correctness and fix any issues before committing.

Access `glean-docker` for local development and testing of the Glean API here: 

- .local/glean-docker
