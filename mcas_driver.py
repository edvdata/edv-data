

import os.path

# import requests
import pandas as pd
from mcas_library import *


# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/mcas.aspx")
# report = MCASExtract("https://profiles.doe.mass.edu/statereport/advcoursecomprate.aspx")

# set the output directory
output_directory = "outdir"

# display valid fields
print("getting fields for {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2018']
request_params['ctl00$ContentPlaceHolder1$ddGrade'] = ['AL']
request_params['ctl00$ContentPlaceHolder1$ddSchoolType'] = ['ALL']
request_params['ctl00$ContentPlaceHolder1$ddSubGroup'] = ['AL:AL']

# used this to test for errors
# request_params['ctl00$ContentPlaceHolder1$ddSubGroup23'] = ['SHOOOT']

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
                        # param2['ctl00$ContentPlaceHolder1$ddSubGroup23'] = ['SHOOOT']

                        report.get_report_real(parameters=param2)
                        report.remove_header_row()
                        # now add a year column
                        report.add_column(0, 'Year', '2001')
                        csvfilenamebase = "{}-{}-{}-{}-{}.csv".format(a, b, c, d, e)
                        csvfilenamebase = os.path.join(output_directory, csvfilenamebase)
                        report.write_csv(csvfilenamebase)
except MCASException as e:
    print("Error: {}".format(e))
    exit(-1)
