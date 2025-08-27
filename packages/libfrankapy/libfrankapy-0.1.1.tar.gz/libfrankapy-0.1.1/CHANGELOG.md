# Changelog

This document records all important changes to the libfrankapy project.

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial project structure and basic architecture
- C++ real-time control core implementation
- Python binding layer (pybind11)
- High-level Python API interface
- Shared memory communication mechanism
- Complete documentation and examples
- CI/CD pipeline configuration
- Code quality checking tools

### Changed

- None

### Fixed

- None

### Removed

- None

### Security

- Added complete safety checks and limitation mechanisms

---

## Version Information

### Version Number Format

This project uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible feature additions
- **PATCH**: Backward-compatible bug fixes

### Change Types

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed soon
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes
- **Security**: Security-related fixes

### Release Schedule

- **Major versions**: 1-2 times per year, containing significant architectural changes
- **Minor versions**: Once per quarter, containing new features and improvements
- **Patch versions**: As needed, mainly for bug fixes

### Support Policy

- **Current version**: Full support, including new features and bug fixes
- **Previous major version**: Only security updates and critical bug fixes
- **Older versions**: No longer maintained

---

## Contributing Guidelines

When adding changelog entries, please follow this format:

```markdown
## [Version] - YYYY-MM-DD

### Added
- New feature description (#PR number)

### Changed
- Change description (#PR number)

### Fixed
- Fix description (#PR number)

### Removed
- Removed feature description (#PR number)
```

### Example Entry

```markdown
## [1.1.0] - 2024-03-15

### Added
- Add trajectory interpolation functionality (#45)
- Support custom safety limit configuration (#52)
- New real-time state monitoring API (#58)

### Changed
- Improve error handling mechanism (#47)
- Optimize shared memory performance (#51)

### Fixed
- Fix joint limit checking bug (#49)
- Resolve memory leak issue (#53)

### Deprecated
- Old move_joint method will be removed in v2.0 (#55)
```

---

## Migration Guide

### From v0.x to v1.0

When v1.0 is released, detailed migration guide will be included here.

### Breaking Changes

All breaking changes will be detailed here, including:

- Changed APIs
- Migration steps
- Example code

---

## Acknowledgments

Thanks to all developers and users who have contributed to the libfrankapy project!

Special thanks to:

- [Franka Robotics](https://www.franka.de/) for providing the excellent libfranka library
- [pybind11](https://github.com/pybind/pybind11) community for providing powerful binding tools
- All users who submitted bug reports and feature requests
