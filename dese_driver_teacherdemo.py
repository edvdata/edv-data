from mcas_library import *
from time import sleep

# initialize the extractor object
try:
    report = MCASExtract("https://profiles.doe.mass.edu/statereport/teacherbyracegender.aspx")
except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit()


# the prefix for this report
output_prefix = "STAFF_DIVERSITY_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
print("Requesting fields for URL: {}".format(report.get_url()))
report.print_report_options()
# quit()
# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['DISTRICT', 'SCHOOL'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2023'],
    'ctl00$ContentPlaceHolder1$ddDisplay': ['NUM'],
    'ctl00$ContentPlaceHolder1$ddClassification': ['1100']
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    classification = params.get('ctl00$ContentPlaceHolder1$ddClassification', 'Unknown Classification')
    report_file.add_column(0, 'Year', year)
    report_file.add_column(0, 'Classification', classification)
    print(f"Modified report to add year: {year} and classification: {classification}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)

