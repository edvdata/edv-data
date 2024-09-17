from mcas_library import *
from time import sleep

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/nextgenmcas.aspx")

# the prefix for this report
output_prefix = "MCAS_NEXTGEN_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL', 'DISTRICT']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2023']
request_params['ctl00$ContentPlaceHolder1$ddGrade'] = ['03', '04', '05', '06', '07', '08', '10', 'AL']
request_params['ctl00$ContentPlaceHolder1$ddSubGroup'] = ['100', '201', '202', '601', '602', '501', '502', '503', '504', '505', '506', '507', '801', '401', '301', '302']

print("Requesting following parameters: ")
for req_param in request_params:
    print("request_params['{}'] = {}".format(req_param, request_params[req_param]))

try:
    param2 = dict()
    for a in request_params['ctl00$ContentPlaceHolder1$ddReportType']:
        for b in request_params['ctl00$ContentPlaceHolder1$ddYear']:
            for c in request_params['ctl00$ContentPlaceHolder1$ddGrade']:
                for d in request_params['ctl00$ContentPlaceHolder1$ddSubGroup']:
                    param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
                    param2['ctl00$ContentPlaceHolder1$ddYear'] = b
                    param2['ctl00$ContentPlaceHolder1$ddGrade'] = c
                    param2['ctl00$ContentPlaceHolder1$ddSubGroup'] = d

                    sleep(12)

                    print("Requesting following parameters: ")
                    for req_param in param2:
                        print("request_params['{}'] = {}".format(req_param, param2[req_param]))

                    report.check_parameters = False
                    report.get_report_real(parameters=param2)
                    report.remove_header_row()
                        
                    # now add necessary columns
                    report.add_column(0, 'Year', b)
                    report.add_column(1, 'Grade', c)
                    report.add_column(2, 'SubGroup', d)

                    csvfilenamebase = "{}-{}-{}-{}.csv".format(a, b, c, d)
                    csvfilenamebase = os.path.join(output_directory, a, b, csvfilenamebase)
                    report.write_csv(csvfilenamebase)
except MCASException as z:
    print("MCASExtract Error: {}".format(z))
    exit(-1)
