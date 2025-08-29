# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.1] - 2025-08-22
## Added
- Support for Python 3.13

## Fixed
- The data validation used in `auto_run` now also validates boolean values for the output column if `kind`=`auto`.
- The `roc_auc_score` now uses the `np.trapezoid` function from newer numpy versions, if available, falling back to `np.trapz`.
- `plot_response_2d` now plots the correct color for dots for dataframes with only one of two binary outcomes represented. Previously, positive outcomes would be mistakenly plotted as negative if no negative outcomes were present.

## [3.4.0] - 2024-06-04

## Added
- `auto_run` and `sample_models` now automatically determines the kind of model to train based on the stypes if `kind`=`auto`. If the output does not have an stype, it falls back to previous default behaviour of `kind`=`regression`.
- Dataframes where the output column has the dtype of `bool` are now supported without first converting the type to `int` or `float`.
- Added function `flip_cmap` to Theme, which reverses a specified colormap belonging to a Theme.
- Added shorthand function `flip_diverging_cmap` to Theme, which reverses the `feyn-diverging` cmap used by default in `plot_response_2d` and `plot_probability_scores`.
- Added new colormap - `feyn-signal` - which is used in the signal plots and other 0-centered rendering that need a colorbar. It defaults to the same gradient as `feyn-diverging` but is not affected by the flip function above.

## Changed
- The limits for when `infer_stypes` considers a numerical series likely to be ordinal or nominal have been tightened to make it more conservative in its attribution.
- Numerical binary input columns are now auto-assigned stypes `numerical` rather than `categorical` when using `infer_stypes`.
- Model graph representations now read `linear` or `logistic` on the output node instead of `out`.
- Fixed the minimum dependency on matplotlib to 3.7.x.
- Theme is now accessible from the top-level package.
- `plot_probability_scores` now uses the `feyn-diverging` cmap boundary colors to plot the negative and positive classes instead of the theme's color cycler.
- Increased the size of the markers in `plot_response_2d`, and styled them to be easier to distinguish from the background.
- `plot_probability_scores` now uses the theme-specific edge color for higher contrast for the bars.

## Fixed
- Fixed a bug where removing variables from a dataframe could result in an error during fitting if the `QLattice` instance had already been used to fit on the full data.
- Fixed a bug where the axis labels for the 2D response plot would not always be vertical when they needed to be.
- `expand_auto_run` now uses the same random seed as provided to the QLattice, if any.
- `plot_response_1d` is now able to compute for models with boolean input features without requiring the user to cast to `int` on their own.
- `Theme.cycler(idx)` now correctly cycles if you overflow the length of the cycler.
- Reference models now contain a `kind` attribute, allowing their use with plots that have kind restrictions again.

## [3.3.1] - 2024-04-24

### Fixed
- Fixed an issue causing `plot_model_response_auto` to fail when fixing categorical inputs.

## [3.3.0] - 2024-04-22

### Added
- Added a new function - `plot_model_response_auto`. This plot inspects the model and automatically determines which inputs to display in the plot and which to fix. It also chooses the appropriate response plot to display.
  - This function can also be accessed directly on the model instance as `plot_response_auto`.
- Added support for the upcoming release of `numpy` 2.0.0 based on the api of release candidate 1. You can read more about the coming changes to `numpy` [here](https://numpy.org/devdocs/release/2.0.0-notes.html)

### Fixed
- Fixed a typo in the ax label for `model.plot_probabilities`.
- Fixed an issue where using the `int16` dtype would result in a `ValueError: data contains nan or infinite values`. The `int16` dtype is now properly accepted. Future errors for unsupported types will now reflect that a type in the data is unsupported.


## [3.2.0] - 2024-02-26

### Added
- `auto_run` will now try to automatically infer the `stypes` based on the dataset if no `stypes` are provided as argument. It will additionally produce warnings for some data types and skip training on redundant or unsupported data types like ID columns and dates.
  - `feyn.tools.infer_stypes` as used by `auto_run` is accessible to use on its own.
  - `stype`: `skip` has been added as an internal meta type to indicate columns to skip during sampling. This behaviour is internal and is subject to change, and we recommend removing the columns from the dataframe instead of relying on this.
- `plot_probability_scores` now supports adding custom legend labels and legend positioning. The legend can also be turned off by specifying `legend_loc=None`. It also now has a title.
- `plot_segmented_loss` now supports adding custom legend labels and legend positioning. The legend can also be turned off by specifying `legend_loc=None`. It also now has a title.
- `plot_model_response_2d` now has a legend that explains the scatter and displays the fixed values. It also now supports specifying the cmap to use.

### Changed
- When using plots and metrics that only work for classifiers on the model instance, they will now return a TypeError if the model is not a classifier. Functions changed are `model.plot_roc_curve`, `model.plot_pr_curve`, `model.plot_probability_scores` and `model.plot_confusion_matrix`, along with metrics `model.roc_auc_score`, `model.accuracy_score` and `model.accuracy_threshold`


### Fixed
- Fixed an issue with some input types not working in the experimental interactive response_1d plot.
- `plot_probability_scores` now uses the proper theme colors for negative and positive classes.
- Fixed a bug when using non-protected functions where the exponential function would result in an error.

## [3.1.0] - 2024-01-22

### Added
- `feyn.tools.split` now supports stratification on one or more columns using the `stratify` parameter. It will additionally raise an exception if the chosen splits are not supported and produce warnings especially on small datasets if the ratios deviate significantly from the expectations.

### Changed
- Deprecated function `connect_qlattice` is no longer included in \* imports. It will be removed in a future major release.
- Methods that plot in SVG, such as `model.savefig`, `plot_signal` and `plot_flow` now all consistently return an SVG wrapper that can be saved to file and is displayable in Jupyter environments.
- Methods that would call `print` or `warnings.warn` now use appropriate python logging instead. It will honor existing logging configurations, however if the logging framework is not configured prior to importing feyn (like in Jupyter notebook use cases), it will register a handler to stdout and default to log messages at the INFO level.
- Various functions that had support for dicts of numpy arrays rather than pandas DataFrames now produce a deprecation warning if you use them like that:
  - `feyn.tools.split`
  - `feyn.metrics.get_pearson_correlation`
  - `feyn.metrics.get_spearmans_correlations`
  - `feyn.metrics.get_mutual_information`
  - `feyn.metrics.segmented_loss`
- More informative error messages are added to some functions if there's a mismatch between the provided DataFrame and model:
  - `feyn.plots.plot_model_summary`
  - `feyn.plots.plot_model_signal`
  - `feyn.plots.plot_segmented_loss`
  - `feyn.plots.plot_model_response_2d`
  - `feyn.plots.plot_activation_flow`
  - `feyn.metrics.get_pearson_correlation`
  - `feyn.metrics.get_spearmans_correlations`
  - `feyn.metrics.get_mutual_information`
  - `feyn.metrics.segmented_loss`
  - `feyn.metrics.get_summary_information`

### Fixed
- Methods that plot in SVG and HTML, such as `model.plot`, `savefig` `plot_signal` and `plot_flow` now all have consistent save behaviour.
- Various internal modules and functions now have proper internal names for a more consistent public API.
- Various public methods that were missing docstrings now have docstrings.

### Removed
- We've removed typing_extensions as a dependency, as it is no longer needed.

## [3.0.6] - 2023-11-27

### Added
- Add support for Python 3.12

### Fixed
- Support for macOS should now be more consistent across python versions, especially regarding M1 builds for macOS 11 and above.
- Extended the support for fitting on DataFrames with ExtensionArray and StringArray types. Note, that some extension types may incur an extra performance cost at this time if they're not numpy-based (like PyArrow backed arrays).
- The tick markers for plot_response_2d are now more well-behaved for very small values

## [3.0.5] - 2023-01-03

### Fixed

- Fixed weird error from having an input name that contains a column, eg `weird:name`. The user is now directed to rename their input columns.
- Fixed slow computation for mutual information on wide datasets.
- Fixed inability to fit on DataFrames with underlying StringArray containers.

## Changed

- Add support for Python 3.11

## [3.0.4] - 2022-09-27

### Fixed

- Fixed matploblib dependency bug introduced with latest release. Now Feyn requires matplotlib >= 3.6.0.
- Fixed loading old serialized models. Introduced migration logic which notifies user to update their models before next release.

## [3.0.3] - 2022-09-22

### Fixed

- Fixed bug with using boolean variables as input features.

### Changed

- Droped support for Python-3.7.

## [3.0.2] - 2022-06-28

### Fixed

- When sample_weights are used to fit models then `feyn.Model.loss_value` computes the weighted mean loss. That means that weighted mean loss is used again for sorting models when `sample_weights` argument is passed to `feyn.fit_models()` or `feyn.QLattice.auto_run()`.

## [3.0.1] - 2022-04-27

### Changed

- Use of `feyn` is now fully local, using an improved and lightweight version of the `QLattice` bundled within `feyn`.
- You should now use `feyn.QLattice()` to get a `QLattice`. Notice that the previous functions `feyn.connect_qlattice()` and `ql.reset()` are now deprecated. They have been updated to match the new workflow to ensure previous code still works as intended, but will be removed in future releases of `feyn`.

### Fixed

- `plot_response_1d` on a single-feature model no longer requires the `by` argument.
- `plot_activation_flow` now warns the user when more than one sample is given.
- Updated outdated LICENSE file

## [2.1.5] - 2022-03-25

### Changed

- `sklearn` and `sympy` is now a dependency of `feyn`.

### Fixed

- `plot_roc_curve` now correctly computes for large datasets.
- Minor performance improvements to the training.

## [2.1.4] - 2022-01-13

### Fixed
- Release windows versions missing in release 2.1.3.

## [2.1.3] - 2022-01-11

### Changed
- Build for python 3.10 for all major platforms.
- Drop support for python 3.6.

### Fixed
- Fixed an issue with `np.float128` type not supported on windows machines. Defaults to `numpy.longdouble`.

## [2.1.2] - 2021-12-10

### Added
- `feyn.reference` models now perform automatic categorical preprocessing. This is done using the optional `stypes` parameter in the constructor.

### Changed
- `feyn.plots.plot_model_response_2d` now has a fixed scale for classification to make it easier to read and compare.

### Fixed
- Fixed an issue where `feyn.tools.estimate_priors` would incorrectly rank the priors in some instances.
- The type checker now allows all numerical numpy dtypes in place of "float" and all integer types for "int", so you no longer have to upcast your dataframes.
- Input name truncation in the model plots now don't truncate if the length would result in a same-length or longer string.

## [2.1.1] - 2021-10-27

### Added
- Sympify:
    - `feyn.tools.sympify()` (also `model.sympify()`) now has parameter `symbolic_cat` that allows you to expand categories to their linear components to make it easier to port or evaluate a sympy expression.
    - `feyn.tools.get_sympy_substitutions` for easily converting a model and a sample to a substitution dictionary for use with `<sympy_expr>.evalf(subs=...)` with the new category changes.
- Exposed convenience functions used by `auto_run` to make it more composable by the user:
    - `feyn.tools.infer_available_threads` tries to guess how many threads you can use. Returns maximum - 1.
    - `feyn.tools.get_progress_label` gives a label for use with `model.show` that displays epoch count and an estimated time to finish (if elapsed seconds are given).
- Experimental feature for IPython environments only: `ql.expand_auto_run` is a function that takes all the same parameters as `auto_run` and creates a runnable code cell with the same code that makes it easier for you to fold out an `auto_run` loop to its primitive components. Note that this contains all of the error handling, general checking and safety measures of `auto_run` that you might not need, but could serve as a starting point.
- Added `model.plot_pr_curve()` to plot precision-recall curves.
- Added `feyn.tools.estimate_priors` function for computing prior probabilities of inputs based on mutual information.
- Added `ql.update_priors` function primitive for updating the QLattice with prior probabilities of inputs.

### Changed
- `feyn.get_diverse_models` is now more likely to return up to n models, and has improved runtime.
- `feyn.tools.get_model_parameters` returns a slightly different structure for categories now. The category is the index, and the weight columns are now named as `{input_name}\[_ix\]}`. This makes it easier to relate to the specific places in the model, for example for use in substituting values in the sympy expression.
- `model.inputs` now returns a unique list of input names.
- The target parameter of models from `feyn.reference` has been renamed `output_name`.

### Fixed
- Sympify model bugs:
    - Numerical input names now work correctly again.
    - Categorical input names are now identifiable if multiple inputs exist in a model with the same name.
    - Input names with sympy reserved characters should be better supported now (the characters get replaced).
- You can now install optional dependencies using `pip install feyn[extras]`
- Fix display of inputs in models that would sometimes result in hard to copy input names.
- Models with categorical registers should now be reproducible with seed and same version of feyn/qlattice.

## [2.1.0] - 2021-09-27

### Added
- Add `feyn.get_diverse_models`. User facing function to get diverse models given their lineage in the QLattice.
- Add `feyn.tools.get_model_parameters` (also `model.get_parameters`). User can extract the parameters of a certain feature in the model as a pandas DataFrame.
- Add option to save various plots:
    - `plot_model_summary` (also `model.plot`) plot as an html file.
    -  plots in the majority of plotting functions.
- Add option to change the figsize of plots in the majority of plotting functions.
- Add more useful display of inputs in model when they share a common beginning.

### Changed
- New QLattice algorithm that vastly improves performance and has better traversal of the search space:
    - `QLattice.update` now expects you to give all the `models` you have - sorted by your metric of choice - and it will figure out how best to update on its own.
    - New format for saving and loading models. Breaks backwards compatibility with previously saved models.
    - `feyn.prune_models` no longer supports `dropout` and `decay` parameters.
- `plot_model_summary` (also `model.plot`):
    - Is intended to plot the most useful metrics and report for your final model, and has been changed to reflect this.
    - Now displays a table of the inputs used in the model.
- `plot_model_signal` (also `model.plot_signal`) no longer plots the summary metrics, and the arguments have changed to reflect this.
- `plot_partial_2d` now has a deprecation warning, use `plot_model_response_2d` (`model.plot_response_2d`) instead.
- `auto_run`:
    - Now sorts best models based on the Bayesian information criterion (BIC) by default rather than loss.
    - No longer returns multiple models with identical mathematical expressions. This means that any number between one and ten models will be returned.
    - Now estimates a time to completion.
    - Starting models are now copied before being added to the fitting loop, meaning that your original models are left unchanged.

### Removed
- Remove `feyn.best_diverse_models`. Replaced by `feyn.get_diverse_models` which has similar functionality.
- Remove semantic type "bool" which previously only used functions add, multiply, gaussian2. We now recommend using the numerical semantic type instead.
- Remove deprecated `plot_partial`. This functionality is covered by `plot_model_response_1d`.

### Fixed
- `auto_run` has been reprimanded and will now properly honor your selected amount of `threads`.
- The query language can now be used in all cases - there is no longer a limitation to which queries will be feasible.

## [2.0.7] - 2021-08-20

### Added

- More informative error messages and type checks for all top-level functions, such as:
  - Primitives:
    - `ql.auto_run`,
    - `ql.sample_models`,
    - `feyn.sample_models`,
    - `feyn.fit_models`,
    - `feyn.prune_models`,
    - `feyn.best_diverse_models`,
    - `ql.update`,
  - Plotting:
    - `feyn.plots.plot_partial2d`,
    - `feyn.plots.plot_roc_curve`,
    - `feyn.plots.plot_probability_scores`,
    - `feyn.plots.plot_activation_flow`,
    - `feyn.plots.plot_model_summary`,
    - `feyn.plots.plot_model_response_1d`,
    - `feyn.plots.plot_residuals`,
    - `feyn.plots.plot_regression`
- `Model.predict` can now accept `pd.Series`.
- New function added called `Model.plot_signal`. This displays signal flow through model. This is the previous behaviour of `Model.plot`.
- New function `make_regression` and `make_classification` functions available in `feyn.datasets` module. These are wrappers of the sklearn functions in `sklearn.datasets`.
- Feyn now has a native package for Mac with Apple silicon (M1 chip) for Python 3.8 and 3.9

### Changed

- `plot_probability_scores` parameter `h_kwargs` has been replaced with `**kwargs`. Now you can pass histogram kwargs as keyword arguments and not a dictionary
- `Model.plot` now displays performance figures underneath the model signal. For regressors these are:
  - `plot_regression`,
  - `plot_residuals`.
For classifiers these are:
  - `plot_roc_curve`,
  - `plot_confusion_matrix`.

### Removed

- `ql.snapshots` have been removed and the `QLattice` no longer has backup and restore functionality.


## [2.0.4] - 2021-07-07

### Changed

- `plot_partial` is now called `plot_response_1d` (`feyn.plots.plot_model_response_1d`)
    - The named argument `fixed` is now called `input_constraints`
    - `plot_partial` can still be called but now raises a FutureWarning about being deprecated.

## [2.0.1] - 2021-06-29

### Changed

- `model.plot` (`feyn.plots.plot_model_summary`) has been updated:
    - The named argument `test` is now called `compare_data`
    - Now supports `labels` param for custom labels for the summary metrics
    - Now supports a list of `compare data`, if you want to compare multiple things
    - Any additional metric added will be a more condensed column to make it easier to compare with the primary metrics

### Fixed

- Model graphs being cut off by jupyter's viewport in some instances should now be fixed by automatic rescaling to fit in view.

## [2.0.0] - 2021-06-18

### Changed

- `Graph` is now called `Model`
- The `QGraph` no longer exists. Instead you now work on lists of `Model`s.
- No longer directly instantiate a `QLattice`. Instead you call `feyn.connect_qlattice()`.
- The common `feyn` workflow is now contained in one function called `auto_run` which lives on a connected `QLattice`.

- In addition to the above automatic workflow, we now have a more expressive set of functions to replace the old:
  - A list of `Model`s can now be sampled from a connected `QLattice` using `sample_models`. This replaces part of the behaviour of the previous `get_regressor` and `get_classifier` on the `QGraph`.
  - You now fit a list of `Model`s using `feyn.fit_models`. This takes a list of `Model`s as an input and returns a list of fitted `Model`s. This replaces part of the previous fit step on the `QGraph`.
  - You now prune the worst `Model`s from a list using `prune_models`. This replaces part of the previous fit step on the `QGraph`. Default behaviour removes duplicate `Model`s, has a decay function on `Model`s and dropout.
  - You get the best diverse `Model`s using `feyn.best_diverse_models`. This replaces `QGraph.best`.
  - Now that you operate on a list of `Model`s, you have the freedom of using the native python `filter` function.
    - You still have a list of useful `feyn.filter` functions but instead apply to the native python `filter`. These functions are. Refer to the documentation for more details:
      - `Complexity`
      - `ContainsInputs`
      - `ExcludeFunctions`
      - `ContainsFunctions`
  - You can display a `Model` as a graph using the `show_model` function.
    - `show_model` detects whether you are in a `Jupyter` environment and decides what to display.

- Other changes:
  - `plot_summary` is now known as `plot` that lives on a `Model`.
  - The output of `sympify` has changed:
    - Categorical input features are now referenced as `<feature_name>_cat`.
    - Numerical input names get suffixed with `_in`.
    - Underscores and spaces in input names are truncated.
  - `sympify` now supports `include_weights=False` which gives an equation without weights and bias.
  - `sympify` now gives consistent results on up to 15 significant digits.
  - `plot_goodness_of_fit` is now called `plot_regression`.
  - `plot_regression_metrics` has been removed - its uses should be covered by `plot_regression`.

### Added

- `plot_roc_curve` has a `threshold` parameter that will plot on the false positive rate and true positive rate at the given `threshold`.
- `plot_confusion_matrix` has a `threshold` parameter.

### Removed

- Our experimental feature module `__future__` has for now outlived its purpose and has been removed.

## [1.6.1] - 2021-05-04
## [1.6.0] - 2021-05-04

### Added

- (__future__) Graph Recorder object that incorporates barcode and feature frequency matrix and heatmaps (now called feature occurrence)

### Fixed

- Fixed a warning from matplotlib about duplicate cmap registering for newer versions of mpl.

## [1.5.6] - 2021-04-23

### Fixed

- Fixed bug in ROC plot function.

## [1.5.5] - 2021-04-21

### Fixed

- Fixed bug in qlattice migration script.

## [1.5.4] - 2021-04-21

### Added

- New sematic type "bool" which will only use functions that makes sense for boolean data types (add, multiply, gaussian2)
- New statistical plots, `plot_goodness_of_fit` and `plot_residuals` to `feyn.plots`.
- New transient QLattice feature.
- `plot summary` improvements:
    - Pearson correlation is now default - and now properly displays negative instead of absolute correlation
    - MI correlation now follows a simple linear colormap that better represents it.
    - Spearman correlation is now available as an alternative correlation function
- Introduce `plot_flow` and a Jupyter-widget-enabled `plot_flow_interactive` for graphs, allowing you to play around with samples and see the activations through the graph.
- (__future__) Barcode plot and feature frequency matrix and heatmap plots.
- Query language available through `feyn.filters` updated
    - New matching starts from the output of the graph.
    - Can write queries using `+` and `*` operators.
    - Wildcards matching any subgraph `_`, complexity can be constrained with edge count in brackets.
- New `show_threshold` parameter in `plot_roc_curve` that colours the ROC curve by thresholds.


## Changed

- Backwards compatability QLattice-urls has been removed from `feyn.QLattice()`. Now the only accepted usages are:
  - `feyn.QLattice(qlattice="<qlattice-id>", api_token="<token>")`.
  - `feyn.QLattice(config="<name of a section in your config file>")`.
  - `feyn.QLattice()  # First section in your config file`.


## [1.5.3] - 2021-03-26

### Changed

- General algorithm improvements.

### Added

- Support for up to 2000 registers (Input features). Previously 200.
- Made it easier to trigger the hover information on graphs in notebooks.

## [1.5.2] - 2021-03-11

### Fixed

- Fixed bug in random seed, which caused QLattice.reset() to always use the same seed.

## [1.5.1] - 2021-03-10

### Changed

- Improve deprecation warning, so that it is obvious how to migrate the old configuration file.

## [1.5.0] - 2021-03-10

### Changed

- The parameters for the QLattice initializer has changed. You now only have to specify the `qlattice` and the `token` instead of the full url.
- With this, also the configuration-file format has changed accordingly. `url` has been replaced by `server` and `qlattice`. The old format still works, but support for it will be removed in a future release. A compatibility warning will be displayed for now.


### Fixed

- plot_partial2d: Fixed to use new contract when getting graph state.


## [1.4.8] - 2021-02-26

### Changed

- The QGraph.fit supports using Akaike Information Criterion (AIC) or Bayesian information criterion (BIC). This may become the default in the future, reducing the need for limiting depth and edges manually
- Default threads used for fitting ans sorting changed from 1 to 4

## [1.4.7] - 2021-02-12

### Changed

- General performance improvements in finding good graphs.

### Added

- Add roc_auc_score to `feyn.metrics` which will calculate the AUC of a graph. (Also accessible on `graph.roc_auc_score`).
- Plotting style improvements:
  - 'light' is now usable as alias to 'default' when setting theme.
  - Matplotlib plot styling now matches the theme choice.
  - Added colormaps to use with matplotlib: 'feyn', 'feyn-diverging'. 'feyn-partial', 'feyn-primary', 'feyn-secondary', 'feyn-highlight', 'feyn-accent'.
- Added `FeatureImportanceTable` to `feyn.insights`. (The equivalent functionality was previous in `pdheatmap` from `__future__`).
- (__future__) Add various stats functions. `graph_f_score` and `plot_graph_p_value`.

## [1.4.6] - 2021-01-08

### Added

- Targeted Maximum Likelihood Estimation (TMLE) introduced in `feyn.inference`. [See more in our docs](https://docs.abzu.ai/docs/guides/advanced/tmle.html)

### Changed

- Default graphs sort back to loss_value instead of bic.
- `feyn.tools.simpify_graph` default option is now to not formulate the logistic function, but instead output “logreg(…)“. Use argument `symbolic_lr=True` if you want to keep previous behavior.
- Categorical variables rendered in the sympify function from category(<X_featurename>) to category_<featurename>.

## [1.4.5] - 2020-12-18

### Added

- Python 3.9 support

### Fixed

- Fix memory bug when handling many registers (>165) in QLattice.

## [1.4.4] - 2020-12-18

### Removed

- `metrics.get_mutual_information()`, `metrics.get_pearson_correlations()`, `metrics.get_summary_information()`. The functionality is now covered by `metrics.calculate_mi()`, `metrics.calculate_pc()` in the public API.

### Changed

- Even more general performance improvements.

## [1.4.3] - 2020-12-04

### Changed

- General performance improvements.

### Added

- `Graph.plot_partial()` and `Graph.plot_partial2d()` to analyze the graph response.
- `metrics.calculate_mi()`, `metrics.calculate_pc()` to calculate mutual information and pearson correlations.

## [1.4.2] - 2020-10-26

- `Graph.sympify()` which returns a sympy expression mathcing the graph
- Mutual information and pearson correlations are now calculated on entire data set, giving more accurate results
- `Graph.fit()` function which can be used to fit or refit a single graph on a dataset
- Adding support to both numerical and categorical partial dependence plots
- Bugfix: 1d plots with categoricals ordered wrt their weights
- Bugfix: Fix support np-dict for graph_summary

## [1.4.1] - 2020-10-09

- Added linear and constant reference models (in `feyn.reference`) to compare with and calculate p-values (lives in `feyn.metrics`).
- Graph vizualizations rewritten and much improved.
- Dark theme support!

## [1.4.0] - 2020-09-03

- ql.update now accepts either a single graph or a list of graphs.
- Added methods: `QLattice.get_regressor` and `QLattice.get_classifier` to replace  `QLattice.get_qgraph`.
- New mathematical functions: `add`, `exp` and `log`.
- You can now control functions in graphs with new filters: `feyn.filters.Functions(["add", "multiply"])` and `feyn.filters.ExcludeFunctions("sine")`.
- New plot. ROC-curves.

## [1.3.3] - 2020-08-14

- Shorthands for plotting and score utility functions on feyn.Graph
- New approach to damping learning rates lead to more accurate fits
- Max-depth filter is less strict on which type of integers it accepts.
- Add automatric retries on failed http-requests
- Configurations can now also be stored in `<home_folder>/.config/.feynrc`

## [1.3.1] - 2020-07-07

- The new automatic scalar is now default on both input and output.
- Alternative input and output semantic types (f#) that does not scaling

## [1.3.0] - 2020-07-06

- Added a new scaler: f$. It is more automatic.

## [1.2.1] - 2020-06-16

- Changed the configuration environment variable `QLATTICE_BASE_URI` to `FEYN_QLATTICE_URL`.
- Changed the configuration environment variable `FEYN_TOKEN` to `FEYN_QLATTICE_API_TOKEN`.
- Support for configuration via config file. `feyn.ini` or `.feynrc` located in your home folder.
- Breaks compatibility with qlattice <= 1.1.2
  - Removed the neeed to add registers via qlattice.registers.get (and removed qlattice.registers.get)
  - New parameter to get_qgraph function to choose the semantic type of the data colums (this replaces the need cat/fixed register types)
- Fixes bug with numpy 1.15 and multiarray import in windows 64bit

## [1.1.2] - 2020-05-11

- Added Windows Support!
- Removed dependency to GraphViz
- Removed dependency to scikit-learn
