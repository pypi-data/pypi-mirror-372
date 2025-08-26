# Changelog

All notable changes to the Kubeflow SDK will be documented in this file.

# [v0.3.0](https://github.com/kubeflow/sdk/releases/tag/v0.3.0) (2025-08-23)

## New Features

- feat(ci): Add GitHub action to verify PR titles ([#42](https://github.com/kubeflow/sdk/pull/42)) by [@andreyvelich](https://github.com/andreyvelich)
- feat(trainer): Add `wait_for_job_status()` API ([#52](https://github.com/kubeflow/sdk/pull/52)) by [@andreyvelich](https://github.com/andreyvelich)
- feat(trainer): Add environment variables argument to CustomTrainer ([#54](https://github.com/kubeflow/sdk/pull/54)) by [@astefanutti](https://github.com/astefanutti)
- feat(trainer): Support Framework Labels in Runtimes ([#56](https://github.com/kubeflow/sdk/pull/56)) by [@andreyvelich](https://github.com/andreyvelich)
- feat(trainer): Add `get_runtime_packages()` API ([#57](https://github.com/kubeflow/sdk/pull/57)) by [@andreyvelich](https://github.com/andreyvelich)

## Bug Fixes

- fix: Expose BuiltinTrainer API to users ([#28](https://github.com/kubeflow/sdk/pull/28)) by [@Electronic-Waste](https://github.com/Electronic-Waste)
- fix(trainer): fix __all__ import. ([#43](https://github.com/kubeflow/sdk/pull/43)) by [@Electronic-Waste](https://github.com/Electronic-Waste)

## Maintenance

- chore(trainer): Remove accelerator label from the runtimes ([#51](https://github.com/kubeflow/sdk/pull/51)) by [@andreyvelich](https://github.com/andreyvelich)
- chore(docs): Add Coveralls Badge to the README ([#53](https://github.com/kubeflow/sdk/pull/53)) by [@andreyvelich](https://github.com/andreyvelich)
- chore(ci): Add dev tests with master dependencies ([#55](https://github.com/kubeflow/sdk/pull/55)) by [@kramaranya](https://github.com/kramaranya)
- chore(ci): Align Kubernetes versions from Trainer for e2e tests ([#58](https://github.com/kubeflow/sdk/pull/58)) by [@astefanutti](https://github.com/astefanutti)
- chore: move pyproject.toml to root ([#61](https://github.com/kubeflow/sdk/pull/61)) by [@kramaranya](https://github.com/kramaranya)

## Other Changes

- Add GitHub issue and PR templates ([#5](https://github.com/kubeflow/sdk/pull/5)) by [@eoinfennessy](https://github.com/eoinfennessy)
- Add Stale GitHub action ([#7](https://github.com/kubeflow/sdk/pull/7)) by [@kramaranya](https://github.com/kramaranya)
- Add pre-commit and flake8 configs ([#6](https://github.com/kubeflow/sdk/pull/6)) by [@eoinfennessy](https://github.com/eoinfennessy)
- Consume Trainer models from external package kubeflow_trainer_api ([#15](https://github.com/kubeflow/sdk/pull/15)) by [@kramaranya](https://github.com/kramaranya)
- Reflect owners updates from KF Trainer ([#32](https://github.com/kubeflow/sdk/pull/32)) by [@tenzen-y](https://github.com/tenzen-y)
- Add CONTRIBUTING.md ([#30](https://github.com/kubeflow/sdk/pull/30)) by [@abhijeet-dhumal](https://github.com/abhijeet-dhumal)
- Step down from sdk ownership role ([#37](https://github.com/kubeflow/sdk/pull/37)) by [@tenzen-y](https://github.com/tenzen-y)
- Add support for UV & Ruff ([#38](https://github.com/kubeflow/sdk/pull/38)) by [@szaher](https://github.com/szaher)
- Update pyproject.toml project links ([#40](https://github.com/kubeflow/sdk/pull/40)) by [@szaher](https://github.com/szaher)
- add e2e notebook tests ([#27](https://github.com/kubeflow/sdk/pull/27)) by [@briangallagher](https://github.com/briangallagher)
- add unit test for trainer sdk ([#17](https://github.com/kubeflow/sdk/pull/17)) by [@briangallagher](https://github.com/briangallagher)
