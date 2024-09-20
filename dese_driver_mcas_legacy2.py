# OLD FILE, DO NOT USE

from mcas_library import *
from time import sleep

def run_request(request_params):
    try:
        param2 = dict()
        for a in request_params['ctl00$ContentPlaceHolder1$ddReportType']:
            for b in request_params['ctl00$ContentPlaceHolder1$ddYear']:
                for c in request_params['ctl00$ContentPlaceHolder1$ddGrade']:
                    for d in request_params['ctl00$ContentPlaceHolder1$ddSchoolType']:
                        for e in request_params['ctl00$ContentPlaceHolder1$ddSubGroup']:
                            param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
                            param2['ctl00$ContentPlaceHolder1$ddYear'] = b
                            param2['ctl00$ContentPlaceHolder1$ddGrade'] = c
                            param2['ctl00$ContentPlaceHolder1$ddSchoolType'] = d
                            param2['ctl00$ContentPlaceHolder1$ddSubGroup'] = e
                            param2['ctl00$ContentPlaceHolder1$hfExport'] = 'Excel'

                            sleep(20)

                            print("Requesting following parameters: ")
                            for req_param in param2:
                                print("request_params['{}'] = {}".format(req_param, param2[req_param]))

                            report.check_parameters = False
                            report.get_report_real(parameters=param2)
                            report.remove_header_row()
                                
                            # now add necessary columns
                            report.add_column(0, 'Year', b)
                            report.add_column(1, 'Grade', c)
                            report.add_column(2, 'SubGroup', e)

                            csvfilenamebase = "{}-{}-{}-{}.csv".format(a, b, c, e)
                            csvfilenamebase = os.path.join(output_directory, a, csvfilenamebase)
                            csvfilenamebase = csvfilenamebase.replace(':', '-')
                            report.write_csv(csvfilenamebase)
    except MCASException as z:
        print("MCASExtract Error: {}".format(z))
        exit(-1)

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/mcas.aspx")

# the prefix for this report
output_prefix = "MCAS_LEGACY_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2012']
request_params['ctl00$ContentPlaceHolder1$ddGrade'] = ['05']
request_params['ctl00$ContentPlaceHolder1$ddSchoolType'] = ['ALL']
# request_params['ctl00$ContentPlaceHolder1$ddSubGroup'] = ['AL:AL', 'ED:N', 'ED:Y', 'HN:Y', 'RA1:01', 'RA1:02', 'RA1:03', 'RA1:04', 'RA1:06', 'RA1:15', 'RA1:20', 'SS:LEP', 'SS:SPED', 'SS:Non-SPED']
request_params['ctl00$ContentPlaceHolder1$ddSubGroup'] = ['AL:AL', 'ED:N', 'ED:Y', 'HN:Y', 'RA1:01', 'RA1:02', 'RA1:03', 'RA1:04', 'RA1:06', 'RA1:15']

print("Requesting following parameters: ")
for req_param in request_params:
    print("request_params['{}'] = {}".format(req_param, request_params[req_param]))
run_request(request_params)

request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2012']
request_params['ctl00$ContentPlaceHolder1$ddGrade'] = ['05']
request_params['ctl00$ContentPlaceHolder1$ddSchoolType'] = ['ALL']
request_params['ctl00$ContentPlaceHolder1$ddSubGroup'] = ['RA1:20', 'SS:LEP', 'SS:SPED', 'SS:Non-SPED']

print("Requesting following parameters: ")
for req_param in request_params:
    print("request_params['{}'] = {}".format(req_param, request_params[req_param]))
run_request(request_params)


