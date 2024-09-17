from mcas_library import *


# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/attendance.aspx")

# the prefix for this report
output_prefix = "ATTENDANCE_REPORT"

# set the output directory
output_directory = "outdir"

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['DISTRICT', 'SCHOOL']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2018', '2019']
request_params['ctl00$ContentPlaceHolder1$ddStudentGroup'] = ['ALL']

print("Requesting following parameters: ")
for req_param in request_params:
    print("request_params['{}'] = {}".format(req_param, request_params[req_param]))

try:
    param2 = dict()
    for a in request_params['ctl00$ContentPlaceHolder1$ddReportType']:
        for b in request_params['ctl00$ContentPlaceHolder1$ddYear']:
            for e in request_params['ctl00$ContentPlaceHolder1$ddStudentGroup']:
                param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
                param2['ctl00$ContentPlaceHolder1$ddYear'] = b
                param2['ctl00$ContentPlaceHolder1$ddStudentGroup'] = e

                print("Requesting following parameters: ")
                for req_param in param2:
                    print("request_params['{}'] = {}".format(req_param, param2[req_param]))

                report.get_report_real(parameters=param2)
                report.remove_header_row()
                # now add a year column
                report.add_column(0, 'Year', b)
                report.add_column(1, 'Subgroup', e)
                thing = report.get_dataframe()
                print("Header column is {}".format(thing.iloc[0]))

                csvfilenamebase = "{}-{}-{}-{}.csv".format(output_prefix, a, b, e)
                csvfilenamebase = os.path.join(output_directory, csvfilenamebase)
                report.write_csv(csvfilenamebase)
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    exit(-1)
