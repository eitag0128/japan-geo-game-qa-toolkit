# OSS Boundary Review

This candidate is safe to publish only if the following remain true.

## Allowed

- generic Python validation logic
- synthetic JSON samples
- documentation about common QA problems
- references to public data categories such as GSI, OSM, PLATEAU, and KSJ
- MIT license for newly written code in this candidate folder

## Not Allowed

- private game source code
- local absolute paths
- private cloud-drive paths
- raw GIS files, map tiles, DEM files, screenshots from licensed sources, or cache files
- database dumps from private production data
- internal issue ledgers or handoff logs
- claims of adoption, stars, or ecosystem importance that are not yet true

## Required Before Publishing

1. Move this folder into a clean public repository.
2. Replace the placeholder GitHub URL in the application draft.
3. Run the tests.
4. Run a secret/path scan.
5. Confirm the license choice.
6. Add a maintainer email or GitHub contact in the public repo.
