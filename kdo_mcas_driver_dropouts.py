# Generate Docstrings for mcas_driver_dropouts.py

from mcas_library import *

# initialize the extractor object
try:
    report = MCASExtract("https://profiles.doe.mass.edu/statereport/dropout.aspx")
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit()

# the prefix for this report
output_prefix = "DROPOUT_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()

# Database columns: school_yr,subgroup,district_name,district_code,total_enrollment,
# total_dropout_num, total_dropout_pct, gr9_dropout_pct, gr10_dropout_pct, gr11_dropout_pct,
# gr12_dropout_pct

# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddSubgroup': ['ALL', 'LEP', 'ED', 'HN', 'FL', 'SWD', 'AA', 'AI',
                                             'AS',
                                             'HI', 'MR', 'NH', 'WH'],
}


# use a custom function to modify the report
def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    if 'EOY' in year:
        year = year.replace('EOY', '')
    report_file.add_column(0, 'Year', year)

    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubgroup', 'Subgroup Not Found')
    student_str = report.map_student_code_to_string(subgroup)
    report_file.add_column(1, 'subgroup', student_str)

    print(f"Modified report to add year: {year} and subgroup: {subgroup}")


''' Start of main driver'''

try:
    sleep_time = 5
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)
