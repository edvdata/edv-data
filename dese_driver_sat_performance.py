from mcas_library import *

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/sat.aspx")

# the prefix for this report
output_prefix = "SAT_PERFORMANCE_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over

request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT', 'SCHOOL'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddStudentGroup': ['ALL', 'LEP', 'LOWINC', 'SPED', 'HIGH', 'AI', 'AS',
                                                 'BL', 'HS', 'MR', 'HP', 'WH', 'F', 'M']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    student_group = params.get('ctl00$ContentPlaceHolder1$ddStudentGroup', 'Unknown Student Group')
    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'StudentGroup', student_group)
    print(f"Modified report to add year: {year} and student group: {student_group}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)
