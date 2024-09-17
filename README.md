# mcas_dese_extractor

This is the MCAS/DESE Extractor project, created for Boston Schools Fund 
by Kurt Overberg (kurt.overberg@gmail.com) at Xrtic Consulting.

This tool allows the user to interact with the Massachusetts Comprehensive Assessment System.  The MCAS is a series 
of forms on websites that outputs data on Massachusetts schools.  This system is broken down into two parts:

1. The MCASExtractor class - Python container class used for accessing MCAS forms and the website.
2. The driver files - These are individual python scripts that contain the information being requested from the 
MCAS report in question.  These driver scripts decide which parameters to request and how to process the output 
of the request.  Generally speaking, processing may include adding columns or deleting rows and writing out CSV files of the data.

To install the MCAS/DESE Extractor:

0. Make sure you are in the mcas_extractor directory.
1. Create a virtual environment: python3 -m venv venv
2. Activate the virtual environment: source venv/bin/activate
3. Install the dependencies: pip install -r requirements.txt
4. Run the individual reports like this: "python3 <driver_file>.py"
5. The output files will be written to the outdir/ directory.

When the script runs it will look at the URL in the driver file and download the report.
It will analyze the report and output a list of valid parameters for that report.  So, for example, when 
you run ght python3 dese_driver_graduation.py file, your output will look like this:

$ python3 dese_driver_graduation.py
Showing possible options for page https://profiles.doe.mass.edu/statereport/gradrates.aspx
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['DISTRICT', 'SCHOOL']
request_params['ctl00$ContentPlaceHolder1$hfExport'] = Excel
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006']
request_params['ctl00$ContentPlaceHolder1$ddRateType'] = ['4-Year:REG', '4-Year:ADJ', '5-Year:REG', '5-Year:ADJ']
request_params['ctl00$ContentPlaceHolder1$ddSubgroup'] = ['5', '11', '10', '153', '95', '156', '12', '157', '9', '99', '87', '86', '88', '89', '92', '91', '90']

...this is to allow you to see what all possible options are for this report.  You can then edit 
the driver file to specify which options to request like this:

request_params = dict()
request_params['ctl00$ContentPlaceHolder1$ddReportType'] = ['DISTRICT']
request_params['ctl00$ContentPlaceHolder1$ddYear'] = ['2021', '2022']
request_params['ctl00$ContentPlaceHolder1$ddRateType'] = ['4-Year:REG']
request_params['ctl00$ContentPlaceHolder1$ddSubgroup'] = ['10', '11']

...so running this driver will request DISTRICT level information for the years 2021 and 2022 
for 4-year:REG ratetype and for subgroups 10 and 11.


Things to be aware of:

- You may see sleep(2) commands in the driver files.  This causes the program to pause for two seconds.
	These are to prevent requesting too many reports at once.
	If running a driver file is taking a long time, you may be triggering a security 
	measure (anti-DenialOfService attack) on the MCAS website and it may blacklist your IP Address temporarily.  
	Try increasing the sleep time, or take a longer time between driver runs.

- These scripts have been tested against Python 3.12.1



