from mcas_library import *

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/gradrates.aspx")

# the prefix for this report
output_prefix = "GRADUATION_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()


# Set the parameters we'd like to loop over
# 'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],

request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddRateType': ['4-Year:REG'],
    'ctl00$ContentPlaceHolder1$ddSubgroup': ['5', '88','87', '11', '12', '89', '153', '10',
                                             '86','92', '91', '99', '90', '95']
}

student_codes = {
    '5': 'All Students',
    '88': 'Asian',
    '87': 'Black',
    '11': 'Female',
    '12': 'High Needs',
    '89': 'Hispanic/Latino',
    '153': 'Low Income',
    '10': 'Male',
    '86': 'Native American/Alaskan Native',
    '92': 'Multi-Race, Non-Hispanic',
    '91': 'Native Hawaiian/Pacific Islander',
    '99': 'SWD',
    '90': 'White',
    '95': 'EL',
}
#
#
# # Set the parameters we'd like to loop over
# request_params = {
#     'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
#     'ctl00$ContentPlaceHolder1$ddYear': ['2013', '2014', '2015', '2016', '2017', '2018', '2019',
#                                          '2020', '2021', '2022'],
#     'ctl00$ContentPlaceHolder1$ddRateType': ['4-Year:REG'],
#     'ctl00$ContentPlaceHolder1$ddSubgroup': ['10', '11']
# }
#
# student_codes = {
#     'ALL': 'All Students',
#     'AS': 'Asian',
#     'AA': 'Black',
#     'FE': 'Female',
#     'HN': 'High Needs',
#     'HI': 'Hispanic or Latino',
#     'FL': 'Low Income',
#     'MA': 'Male',
#     'AI': 'Native American/Alaskan Native',
#     'MR': 'Multi-Race, Non-Hispanic',
#     'NH': 'Native Hawaiian/Pacific Islander',
#     'SWD': 'Students with disabilities',
#     'WH': 'White'
# }


def map_student_code_to_string(code):
    return student_codes.get(code, "Unknown")


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubgroup', 'Unknown Subgroup')

    mapped_subgroup = map_student_code_to_string(subgroup)
    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'Subgroup', mapped_subgroup)
    print(f"Modified report to add year: {year} subgroup: {mapped_subgroup}")

#
# request_params = dict()
# request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['SCHOOL', 'DISTRICT']
# request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']
# request_params['ctl00$ContentPlaceHolder1$ddRateType'] = ['4-Year:REG']
# request_params['ctl00$ContentPlaceHolder1$ddSubgroup'] = ['10', '11']


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except Exception as e:
    print(e)
