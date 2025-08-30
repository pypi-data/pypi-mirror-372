import pandas as pd
import itertools
from tidypath import SavedataSkippedComputation
from . import pd_utils

def summarize_results(combinations_dict, compute_function, analyze_function, result_idx=0, metric_label='metric'):
    """
    Returns a pandas Series with the results of the analysis.

    combinations_dict: dict of lists. Each key is a parameter name and each value is a list of possible values for that parameter.
    compute_function: function that computes the results. It should take as input the parameters in combinations_dict and return the output to pass to analyze_function.
    analyze_function: function that takes the output of compute_function and returns the metrics to be saved.
    result_idx: index of the result to be analyzed. If None, the whole result is passed to analyze_function.
    metric_label: name of the metric to be saved.
    """
    result = {}

    # Generating all combinations of parameters
    keys, values = zip(*combinations_dict.items())
    keys_label = [k for k, v in combinations_dict.items() if len(v) > 1]
    for combination in itertools.product(*values):
        kwargs = dict(zip(keys, combination))

        # Perform the computation (compute_function should be defined by you)
        report = compute_function(**kwargs, skip_computation=True)
        is_computed = not isinstance(report, SavedataSkippedComputation)

        if is_computed:
            if result_idx is not None:
                report = report[result_idx]
            metrics = analyze_function(report)
            # Update results dictionary
            def process_key(key):
                if isinstance(key, (list, tuple)):
                    return "+".join(key)
                else:
                    return key
            result_key = tuple([process_key(kwargs[key]) for key in keys_label])
            for metric_name, metric_value in metrics.items():
                result[(*result_key, metric_name)] = metric_value
        else:
            continue
    result = pd.Series(result)
    if result.size > 0:
        result.index.set_names(keys_label + [metric_label], inplace=True)
    return result

def CI_report(df, df_CI, ndigits=2):
    """
    Returns a df containing the sample statistic and its CI between parentheses.
    """
    df_joint = pd_utils.tuple_wise(df, df_CI)
    def format_CI(x):
        ss, ci = x
        return f"{ss:.{ndigits}f} ([{ci[0]:.{ndigits}f}, {ci[1]:.{ndigits}f}])"
    return df_joint.applymap(format_CI)
