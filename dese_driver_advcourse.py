from time import sleep

from mcas_library import *


# SWD = Students with disabilities?
# EL = English learner?
# subgroup mapping
options_dict = {
    "5": "All Students",
    "9": "Low Income",
    "10": "Male",
    "11": "Female",
    "12": "High Needs",
    "86": "Native American/Alaskan Native",
    "87": "Black",
    "88": "Asian",
    "89": "Hispanic/Latino",
    "90": "White",
    "91": "Native Hawaiian/Pacific Islander",
    "92": "Multi-Race, Non-Hispanic",
    "95": "LEP English learner",
    "99": "SWD"
}


# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/advcoursecomprate.aspx")

# the prefix for this report
output_prefix = "ADV_COURSE_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over
# NOTE: this form has subgroups with different names than other tables.
#   Also- it appears that subgroup names changed over the years, so if you
#         select 2020 for the year, subgroup 153 appears in the options as "Economically Disadvantaged",
#         which should map to 'low income' but they have different codes.
# ALSO- Depending on the year you choose, the page dynamically reconfigures itself via javascript

request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2022'],
    'ctl00$ContentPlaceHolder1$ddSubgroup': ['5', '153', '12', '95', '99', '87', '86', '88',
                                             '89', '92', '91', '90']
}

def map_subgroup_code_to_string(code):
    return options_dict.get(code, 'Unknown Subgroup')


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubgroup', 'Unknown Subgroup')

    report_file.add_column(0, 'school_yr', year)
    subgroup_translation = map_subgroup_code_to_string(subgroup)
    report_file.add_column(1, 'subgroup', subgroup_translation)

    print(
        f"Modified report to add year: {year} subgroup: {subgroup}")


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
# request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['DISTRICT']
# request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2020', '2021']
# request_params['ctl00$ContentPlaceHolder1$ddSubgroup'] = ['5', '153', '12', '95', '99', '87', '86', '88', '89', '92',
#                                                           '91', '90']

# print("Requesting following parameters: ")
# for req_param in request_params:
#     print("request_params['{}'] = {}".format(req_param, request_params[req_param]))
#
# try:
#     param2 = dict()
#     for a in request_params['ctl00$ContentPlaceHolder1$ddReportType']:
#         for b in request_params['ctl00$ContentPlaceHolder1$ddYear']:
#             for c in request_params['ctl00$ContentPlaceHolder1$ddSubgroup']:
#                 param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
#                 param2['ctl00$ContentPlaceHolder1$ddYear'] = b
#                 param2['ctl00$ContentPlaceHolder1$ddSubgroup'] = c
#
#                 sleep(0.5)
#
#                 print("Requesting following parameters: ")
#                 for req_param in param2:
#                     print("request_params['{}'] = {}".format(req_param, param2[req_param]))
#
#                 report.check_parameters = False
#                 report.get_report_real(parameters=param2)
#                 report.remove_header_row()
#
#                 # now add necessary columns
#                 report.add_column(0, 'Year', b)
#                 report.add_column(1, 'Subgroup', c)
#
#                 csvfilenamebase = "{}-{}-{}.csv".format(a, b, c)
#                 csvfilenamebase = os.path.join(output_directory, a, b, csvfilenamebase)
#                 report.write_csv(csvfilenamebase)
# except MCASException as z:
#     print("MCASExtract Error: {}".format(z))
#     exit(-1)
