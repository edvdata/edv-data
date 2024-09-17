from mcas_library import *
import sys

url = "https://profiles.doe.mass.edu/statereport/epppfacultybyracegender.aspx"

if len(sys.argv) > 1:
    print("argv1 is {}".format(sys.argv[1]))
    url = sys.argv[1]

'''
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012']
'''

# initialize the extractor object
report = MCASExtract(url)

# the prefix for this report
output_prefix = "EPPP_FACULTY_BY_RACE_GENDER_REPORT"

# set the output directory
output_directory = "outdir"

# display valid fields
print("The following fields are availble for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2018']

print("\nRunning with the following parameters: ")
for req_param in request_params:
    print("request_params['{}'] = {}".format(req_param, request_params[req_param]))
print("")
try:
    param2 = dict()
    for a in request_params['ctl00$ContentPlaceHolder1$ddYear']:
        param2['ctl00$ContentPlaceHolder1$ddYear'] = a
        param2['ctl00$ContentPlaceHolder1$hfExport'] = 'Excel'

        # print("Requesting the following parameters: ")
        # for req_param in param2:
        #     print("request_params['{}'] = {}".format(req_param, param2[req_param]))

        report.get_report_real(parameters=param2)
        report.remove_header_row()
        # now add a year column
        report.add_column(0, 'Year', a)
        csvfilenamebase = "{}-{}.csv".format(output_prefix, a)
        csvfilenamebase = os.path.join(output_directory, csvfilenamebase)
        report.write_csv(csvfilenamebase)
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    exit(-1)
