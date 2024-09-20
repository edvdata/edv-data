from mcas_library import *

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/nextgenmcas.aspx")

# the prefix for this report
output_prefix = "MCAS_NEXTGEN_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddGrade': ['03', '04', '05', '06', '07', '08', '10', 'AL'],
    'ctl00$ContentPlaceHolder1$ddSubGroup': ['100', '201', '202', '601', '602', '501', '502', '503',
                                             '504', '505', '506', '507', '801', '401', '301', '302']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    grade = params.get('ctl00$ContentPlaceHolder1$ddGrade', 'Unknown Grade')
    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubGroup', 'Unknown Subgroup')

    report_file.add_column(0, 'Year', year)
    report_file.add_column(1, 'Grade', grade)
    report_file.add_column(2, 'Subgroup', subgroup)
    print(f"Modified report to add year: {year} grade: {grade} subgroup: {subgroup}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)
