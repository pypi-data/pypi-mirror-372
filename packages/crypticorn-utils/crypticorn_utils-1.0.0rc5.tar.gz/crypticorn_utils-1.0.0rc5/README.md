This module serves as a central place for providing utilities for our python backends.

- **Auth**: Authentication and authorization for APIs with API key and JWT bearer token support
- **Enums**: Common enumerations for type safety and consistency
- **Errors**: Comprehensive error handling system with HTTP exceptions and error content structures
- **Exceptions**: Custom exception classes and error handling utilities
- **Logging**: Logging configuration and utilities for consistent formatting
- **Middleware**: API middleware components for request/response processing
- **Pagination**: Utilities for paginated API responses and cursor-based pagination
- **Utils**: General utility functions and helper methods

# Changelog

<!-- changelog-insertion -->

## v1.0.0-rc.5 (2025-08-28)

### Features

- Enhance exception handling with improved type safety and restructure imports (breaking)
  ([`c58a5fe`](https://github.com/crypticorn-ai/util-libraries/commit/c58a5fe6fddcb857aedc3cab49473f7edfca66ac))


## v1.0.0-rc.4 (2025-08-27)

### Bug Fixes

- Pass additional arguments as kwargs to .build_exception
  ([`627f88e`](https://github.com/crypticorn-ai/util-libraries/commit/627f88ee35e19770e19e603f7891588bcae9f07e))


## v1.0.0-rc.3 (2025-08-26)

### Features

- Export more classes in init, fix bug in exception handling, remove enums
  ([`4cd659b`](https://github.com/crypticorn-ai/util-libraries/commit/4cd659b4b43fd1231ffc1c2a4dfc6023c691fa7d))

### Refactoring

- Remove partial_model decorator and update documentation references
  ([#5](https://github.com/crypticorn-ai/util-libraries/pull/5),
  [`48bad3d`](https://github.com/crypticorn-ai/util-libraries/commit/48bad3dd6a3b01c9e402d3aee420a04bc0076065))


## v1.0.0-rc.2 (2025-07-31)

### Bug Fixes

- Change verify api key request
  ([`2dee77f`](https://github.com/crypticorn-ai/util-libraries/commit/2dee77f64495b2bf28628194bbd9bc4d0b856294))

### Documentation

- Update Readme
  ([`c2f8eec`](https://github.com/crypticorn-ai/util-libraries/commit/c2f8eec654be4cff89643abec915a5fd3476f1fa))

### Refactoring

- Improve type hinting in partial_model decorator
  ([`de558ba`](https://github.com/crypticorn-ai/util-libraries/commit/de558ba6b495ed4cc9121ac0e34d9460a87c0122))

### Testing

- Fix failing auth test
  ([`5ff77b3`](https://github.com/crypticorn-ai/util-libraries/commit/5ff77b3e49e5348c4c38d329a643a03717cd2db0))


## v1.0.0-rc.1 (2025-07-17)

### Build System

- Deployment config for v1 branches
  ([`b94d9e7`](https://github.com/crypticorn-ai/util-libraries/commit/b94d9e72616e398760993f6ebb1a6fd876a95802))

BREAKING CHANGE: - removed: mixins, openapi and both router modules; CLI; Scope Enum class;
  `throw_if_none` and `throw_if_falsy`; all deprecation warnings - reworked: exceptions and error
  modules

- Mark packaage as typed
  ([`69544a8`](https://github.com/crypticorn-ai/util-libraries/commit/69544a8709f4d55850e107031b82d91c28334b3c))

- Remove support for python versions 3.9 and 3.10
  ([`80b8543`](https://github.com/crypticorn-ai/util-libraries/commit/80b8543ed5559a0de421aef4e2382193e930751a))


## v0.1.0-rc.1 (2025-06-23)

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))

### Features

- Initial release
  ([`4da5fe3`](https://github.com/crypticorn-ai/util-libraries/commit/4da5fe3d33abd31b3b35462e93052db0cde077c2))


## Unreleased

### Documentation

- Add changelog
  ([`788f1f6`](https://github.com/crypticorn-ai/util-libraries/commit/788f1f670a8a50251401ebd1fc9ab7d2ca855a8d))

- Update Readme
  ([`d2b52cf`](https://github.com/crypticorn-ai/util-libraries/commit/d2b52cfe48de7a8b248ceefbc3bc7007ad21ea72))
