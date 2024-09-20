from mcas_library import *

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/gradsattendingcollege.aspx")

# the prefix for this report
output_prefix = "IHE_ATTENDANCE_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()

# Set the parameters we'd like to loop over
request_params = {
    'ddReportType': ['SCHOOL', 'DISTRICT'],
    'ddYear': ['2013', '2014', '2015', '2016', '2017', '2018', '2019',
               '2020', '2021', '2022'],
    'ddStudentGroup': ['ALL', 'LEP', 'ECODIS', 'HIGH', 'LOWINC', 'SPED', 'BL', 'AI', 'AS', 'HS',
                       'MR', 'HP', 'WH'],
    'ddInOutState': ['ALL', 'IN_STATE', 'OUT_OF_STATE'],
    'ddAttendRange': ['MARCH'],
    'ddPctDenomType': ['COLL_ATTEND'],
    'hfExport': ['Excel']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ddYear', 'Unknown Year')
    inoutstate = params.get('ddInOutState', 'Unknown inoutstate')
    studentgroup = params.get('ddStudentGroup', 'Unknown StudentGroup')

    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'InOutState', inoutstate)
    report_file.add_column(2, 'StudentGroup', studentgroup)

    print(f"Modified report to add year: {year} and inoutstate: {inoutstate} and studentgroup: {studentgroup}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)
except Exception as e:
    print(e)
