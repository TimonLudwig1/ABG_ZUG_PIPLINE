from pipelines import *

converted_files = run_dbf_pipeline(
    base_directory="input",
    output_directory="temp",
    data_output_directory="converted_output"
)

filtered_files = run_filter_pipeline(
    base_dir="converted_output",
    output_dir="filtered_output"
)

wj_files = run_wj_pipeline(
    base_dir="filtered_output",
    output_dir="wirtschaftsjahre"
)