from mcas_library import *

# initialize the extractor object
report = MCASExtract("https://profiles.doe.mass.edu/statereport/masscore.aspx")

# the prefix for this report
output_prefix = "MASSCORE_REPORT"
# set the output directory
output_directory = "outdir"
output_directory = os.path.join(output_directory, output_prefix)

# Output available parameters if user passes in -q (query) as an argument
if len(sys.argv) > 1:
    if sys.argv[1] == '-q':
        # display valid fields
        print("Requesting fields for URL: {}".format(report.get_url()))
        report.print_report_options()
        quit()

# Set the parameters we'd like to loop over

request_params = {
    'ctl00$ContentPlaceHolder1$ddReportType': ['SCHOOL', 'DISTRICT'],
    'ctl00$ContentPlaceHolder1$ddYear': ['2022'],
    'ctl00$ContentPlaceHolder1$ddSubgroup': ['ALL', 'FE', 'MA', 'ED']
}

def custom_modify_report(report, params):
    # add custom columns to the report at the report level
    year = params.get('ctl00$ContentPlaceHolder1$ddYear', 'Unknown Year')
    subgroup = params.get('ctl00$ContentPlaceHolder1$ddSubgroup', 'Unknown Subgroup')

    # Add a year columns to the report in the first column,
    # get the year from the ddSubgroup parameter
    report.add_column(0, 'Custom Year', year)

    # Add a subgroup column to the report in the second column
    report.add_column(1, 'Custom Subgroup', subgroup)

    print(f"Modified report with year: {year}, subgroup: {subgroup}")



try:
    sleep_time = 5  # Optional, can be omitted if you want the default
    report.process_reports(request_params, report, output_directory, sleep_time, modify_report_func=custom_modify_report)

except Exception as e:
    print(e)
