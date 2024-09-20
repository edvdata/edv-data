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
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2013', '2014', '2015', '2016', '2017', '2018', '2019',
                                         '2020', '2021', '2022'],
    'ctl00$ContentPlaceHolder1$ddRateType': ['4-Year:REG'],
    'ctl00$ContentPlaceHolder1$ddSubgroup': ['10', '11']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubGroup', 'Unknown Subgroup')

    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'Subgroup', subgroup)
    print(f"Modified report to add year: {year} subgroup: {subgroup}")

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
