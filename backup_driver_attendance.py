from mcas_library import *


# initialize the extractor object
try:
    report = MCASExtract("https://profiles.doe.mass.edu/statereport/attendance.aspx")
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit()


# the prefix for this report
output_prefix = "ATTENDANCE_REPORT"

# set the output directory
output_directory = "outdir"

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT', 'SCHOOL'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2018', '2019'],
    'ctl00$ContentPlaceHolder1$ddStudentGroup': ['ALL']
}

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time)
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)


