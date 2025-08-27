# Changelog

All notable changes to ggoat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation system with Sphinx
- Method chaining API for fluent plot construction
- Support for all major geometric objects (geoms)
- Integration with lets-plot JavaScript rendering
- Jupyter notebook tutorials and examples
- Full Grammar of Graphics implementation

### Changed
- API uses method chaining instead of `+` operator
- Optimized for Pyodide and browser environments
- Minimal dependencies approach

### Fixed
- Data handling for both dict and DataFrame inputs
- Jupyter integration with automatic lets-plot detection

## [0.1.0] - 2024-01-XX

### Added
- 🎉 Initial release of ggoat!
- Core ggplot class with method chaining
- Aesthetic mapping system (aes)
- Basic geometric objects:
  - `geom_point()` - Scatter plots
  - `geom_line()` - Line plots  
  - `geom_bar()` - Bar charts
  - `geom_histogram()` - Histograms
  - `geom_smooth()` - Smoothed conditional means
  - `geom_boxplot()` - Box plots
  - `geom_density()` - Density plots
- Statistical transformations
- Built-in themes:
  - `theme_minimal()`
  - `theme_bw()`
  - `theme_classic()`
  - `theme_grey()`
  - `theme_light()`
  - `theme_void()`
- Scale functions:
  - `scale_color_manual()`
  - `scale_fill_manual()`
  - `scale_color_gradient()`
  - `scale_fill_gradient()`
- Coordinate systems:
  - `coord_cartesian()`
  - `coord_flip()`
  - `coord_fixed()`
  - `coord_polar()`
- Faceting:
  - `facet_wrap()`
  - `facet_grid()`
- Label functions:
  - `labs()`
  - `xlab()`, `ylab()`
  - `ggtitle()`
- Export capabilities:
  - HTML output with JavaScript rendering
  - JSON plot specifications
- Browser optimization:
  - Pyodide compatibility
  - Minimal dependencies
  - lets-plot JavaScript integration
- Documentation:
  - Complete API reference
  - Getting started guide
  - Jupyter notebook examples
  - Advanced tutorials

### Technical Features
- Method chaining for readable syntax
- Immutable plot objects
- Support for Python dictionaries and pandas DataFrames
- Automatic environment detection (Jupyter, Pyodide, etc.)
- Fallback rendering for unsupported environments
- Comprehensive error handling

### Browser Support
- Pyodide/WebAssembly environments
- Jupyter notebooks (classic and JupyterLab)
- JupyterLite (browser-based Jupyter)
- Google Colab
- Standard Python environments

---

**Legend:**
- 🎉 Major feature
- ✨ New feature  
- 🐛 Bug fix
- 📚 Documentation
- 🔧 Refactor
- ⚡ Performance
- 💥 Breaking change