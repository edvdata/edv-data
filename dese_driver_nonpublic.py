from mcas_library import *
from time import sleep

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/nonpublicschoolreport.aspx")

# the prefix for this report
output_prefix = "NONPUBLIC_REPORT"

# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# display valid fields
report.print_report_options()

# Set the parameters we'd like to loop over
request_params = {
    'ctl00$ContentPlaceHolder1$ddYear': ['2022'],
}


def custom_modify_report(report_file, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    report_file.add_column(0, 'Year', year)
    print(f"Modified report to add year: {year}")


''' Start of main driver'''

try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time,
                           modify_report_func=custom_modify_report)

except MCASException as e:
    print("MCASExtract Error: {}".format(e))
    sys.exit(-1)
