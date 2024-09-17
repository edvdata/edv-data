
from mcas_library import *
global reports

init()

reporttype = ['DISTRICT']
grades = ['AL', '03', '04', '05', '06', '07', '08', '10', 'HS']
subg = ['ED:N', 'ED:Y', 'FL:N', 'FL:Y']

# now we can access reports obj
print("reports are: {}".format(reports))
# for a in reports['ctl00$ContentPlaceHolder1$ddReportType']:
for a in reporttype:
    # for b in reports['ctl00$ContentPlaceHolder1$ddYear']:
    for b in [year]:
        for c in grades:
            for d in subg:
                get_mcas_data(report_url, output_directory, a, b, c, school_type, d)
