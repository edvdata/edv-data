from mcas_library import *
import sys
from time import sleep

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/attendance.aspx")

# the prefix for this report
output_prefix = "ATTENDANCE_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over
# 'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2024EOY'],
    'ctl00$ContentPlaceHolder1$ddStudentGroup': ['ALL', 'FE', 'MA', 'HN', 'LEP', 'FL', 'SWD',
                                                 'AA', 'AI', 'AS', 'HI', 'MR', 'NH', 'WH'],
}

# request_params = dict()
# request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL', 'DISTRICT']
# request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2023EOY']
# request_params['ctl00$ContentPlaceHolder1$ddStudentGroup'] = ['ALL', 'FE', 'MA', 'HN', 'LEP', 'FL', 'SWD', 'AA', 'AI', 'AS', 'HI', 'MR', 'NH', 'WH']


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    studentgroup = params.get('ctl00$ContentPlaceHolder1$ddStudentGroup', 'Unknown Student Group')
    # change year to exclude EOY

    # write code to check if year contains 'EOY' remove it from the string
    if year.contains('EOY'):
        year = year.substitute('EOY', '')
    # if year[-3:] == 'EOY':
    #     year = year[:-3]

    report_file.add_column(0, 'Year', year)
    student_str = report.map_student_code_to_string(studentgroup)
    report_file.add_column(1, 'StudentGroup', student_str)
    print(f"Modified report to add year: {year} studentgroup: {studentgroup}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)