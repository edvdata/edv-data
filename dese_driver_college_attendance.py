from mcas_library import *
from time import sleep

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/gradsattendingcollege.aspx")

# the prefix for this report
output_prefix = "IHE_ATTENDANCE_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

if os.path.isdir(output_directory) is False:
    print("Output directory {} does not exist.".format(output_directory))
    quit()


# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()

# request_params['ddReportType'] = ['', 'DISTRICT', 'SCHOOL']
request_params['ddReportType'] = ['DISTRICT']

# request_params['ddYear'] = ['', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004']
request_params['ddYear'] = ['2022']

# request_params['ddStudentGroup'] = ['ALL', 'LEP', 'ECODIS', 'HIGH', 'LOWINC', 'SPED', 'BL', 'AI', 'AS', 'HS', 'MR', 'HP', 'WH']
request_params['ddStudentGroup'] = ['ALL', 'LEP', 'ECODIS', 'HIGH', 'LOWINC', 'SPED', 'BL', 'AI', 'AS', 'HS', 'MR', 'HP', 'WH']

# request_params['ddInOutState'] = ['ALL', 'IN_STATE', 'OUT_OF_STATE']
request_params['ddInOutState'] = ['ALL', 'IN_STATE', 'OUT_OF_STATE']

# request_params['ddAttendRange'] = ['MARCH', '16_MONTH']
request_params['ddAttendRange'] = ['MARCH']

# request_params['ddPctDenomType'] = ['COLL_ATTEND', 'HS_GRAD']
request_params['ddPctDenomType'] = ['COLL_ATTEND']

request_params['hfExport'] = 'Excel'

print("Script getting following parameters: ")
for req_param in request_params:
    print("request['{}'] = {}".format(req_param, request_params[req_param]))

try:
    param2 = dict()
    for a in request_params['ddReportType']:
        for b in request_params['ddYear']:
            for c in request_params['ddStudentGroup']:
                for d in request_params['ddInOutState']:
                    for e in request_params['ddAttendRange']:
                        for f in request_params['ddPctDenomType']:
                            param2['ddReportType'] = a
                            param2['ddYear'] = b
                            param2['ddStudentGroup'] = c
                            param2['ddInOutState'] = d
                            param2['ddAttendRange'] = e
                            param2['ddPctDenomType'] = f
                            param2['hfExport'] = 'Excel'
                            # param2['ctl00$ContentPlaceHolder1$hfExport'] = 'Excel'

                            sleep(10)

                            print("Requesting the following parameters: ")
                            for req_param in param2:
                                print("request_params['{}'] = {}".format(req_param, param2[req_param]))

                            report.check_parameters = False
                            report.get_report_real(parameters=param2)
                            report.remove_header_row()
                                
                            # now add necessary columns
                            report.add_column(0, 'Year', b)
                            report.add_column(1, 'InOutState', d)
                            report.add_column(2, 'StudentGroup', c)

                            csvfilenamebase = "{}-{}-{}-{}.csv".format(a, b, d, c)
                            csvfilenamebase = os.path.join(output_directory, a, b, d, csvfilenamebase)
                            report.write_csv(csvfilenamebase)

except MCASException as z:
    print("MCASExtract Error: {}".format(z))
    exit(-1)
