from mcas_library import *
from time import sleep

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/ap_part.aspx")

# the prefix for this report
output_prefix = "AP_PARTICIPATION_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()

# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddSubject': ['ALL'],
    'ctl00$ContentPlaceHolder1$ddStudentGroup': ['ALL', 'LEP', 'ECODIS', 'LOWINC', 'SPED', 'HIGH',
                                                 'AI', 'AS', 'BL', 'HS', 'MR', 'HP', 'WH', 'F', 'M']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    subject = params.get('ctl00$ContentPlaceHolder1$ddSubject', 'Unknown Subject')
    studentgroup = params.get('ctl00$ContentPlaceHolder1$ddStudentGroup', 'Unknown StudentGroup')

    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'Subject', subject)
    report_file.add_column(2, 'StudentGroup', studentgroup)

    print(
        f"Modified report to add year: {year} subject: {subject} and studentgroup: {studentgroup}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)



# Set the parameters we'd like to loop over
# request_params = dict()
# request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL','DISTRICT']
# request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2023']
# request_params['ctl00$ContentPlaceHolder1$ddSubject'] = ['ALL']
# request_params['ctl00$ContentPlaceHolder1$ddStudentGroup'] = ['ALL', 'LEP', 'ECODIS', 'LOWINC', 'SPED', 'HIGH', 'AI', 'AS', 'BL', 'HS', 'MR', 'HP', 'WH', 'F','M']
#
# print("Requesting following parameters: ")
# for req_param in request_params:
#     print("request_params['{}'] = {}".format(req_param, request_params[req_param]))

# try:
#     param2 = dict()
#     for a in request_params['ctl00$ContentPlaceHolder1$ddReportType']:
#         for b in request_params['ctl00$ContentPlaceHolder1$ddYear']:
#             for c in request_params['ctl00$ContentPlaceHolder1$ddSubject']:
#                 for d in request_params['ctl00$ContentPlaceHolder1$ddStudentGroup']:
#                     param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
#                     param2['ctl00$ContentPlaceHolder1$ddYear'] = b
#                     param2['ctl00$ContentPlaceHolder1$ddSubject'] = c
#                     param2['ctl00$ContentPlaceHolder1$ddStudentGroup'] = d
#
#                     sleep(12)
#
#                     print("Requesting following parameters: ")
#                     for req_param in param2:
#                         print("request_params['{}'] = {}".format(req_param, param2[req_param]))
#
#                     report.check_parameters = False
#                     report.get_report_real(parameters=param2)
#                     report.remove_header_row()
#
#                     # now add necessary columns
#                     report.add_column(0, 'Year', b)
#                     report.add_column(1, 'Subject', c)
#                     report.add_column(2, 'StudentGroup', d)
#
#                     csvfilenamebase = "{}-{}-{}-{}.csv".format(a, b, c, d)
#                     csvfilenamebase = os.path.join(output_directory, a, b, csvfilenamebase)
#                     report.write_csv(csvfilenamebase)
# except MCASException as z:
#     print("MCASExtract Error: {}".format(z))
#     exit(-1)
