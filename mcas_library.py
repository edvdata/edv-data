"""
This module contains the MCAS library, which allows the user to interact with the
Massachusetts Comprehensive Assessment System.

The MCAS library is a Python container class used for accessing MCAS forms and the website.

The library contains the following classes:

- `MCASExtract`: A class used to access MCAS forms and the website.

The library also contains the following functions:

- [process_reports](cci:1:///mcas_library.py:289:4-352:20): A function that
processes reports by looping through all combinations of request parameters, fetching reports, and
saving them as CSV files.
- [write_xlsx](cci:1:///mcas_library.py:260:4-269:29): A function that
writes a Pandas DataFrame to an Excel file.

The library requires the following libraries:

- `beautifulsoup4`
- `certifi`
- `charset-normalizer`
- `et-xmlfile`
- `idna`
- `numpy`
- `openpyxl`
- `pandas`
- `python-dateutil`
- `pytz`
- `requests`
- `six`
- `soupsieve`
- `urllib3`
- `xlrd`

This library was created by Kurt Overberg for Boston Schools Fund (C) 2022 Xrtic Consulting.
"""

import itertools
import os.path
import re
import sys
from io import BytesIO
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup

output_directory = './'
isDebug = False

report_url = ""
extra_fields = {}
session = requests.session()
list_options = False
reports = {}

# create an array based on these codes:
# ALL,All Students
# FE,Female
# MA,Male
# ED,Economically Disadvantaged
# HN,High Needs
# LEP,English learner
# FL,Low Income
# SWD,Students with disabilities
# AA,African American/Black
# AI,American Indian or Alaskan Native
# AS,Asian
# HI,Hispanic or Latino
# MR,Multi-race, non-Hispanic or Latino
# NH,Native Hawaiian or Pacific Islander
# WH,White
student_codes = {
    'ALL': 'All Students',
    'AS': 'Asian',
    'AA': 'Black',
    'FE': 'Female',
    'HN': 'High Needs',
    'HI': 'Hispanic or Latino',
    'FL': 'Low Income',
    'MA': 'Male',
    'AI': 'Native American/Alaskan Native',
    'MR': 'Multi-Race, Non-Hispanic',
    'NH': 'Native Hawaiian/Pacific Islander',
    'SWD': 'Students with disabilities',
    'WH': 'White'
}


# Create a class docstring

class MCASException(Exception):
    """
    Basic MCASException class

    """
    pass


class MCASExtract:
    """
    This class is used to access MCAS forms and the website.

    Attributes:
        selects (dict): A dictionary containing all the select elements found on the form.
        reports (dict): A dictionary containing all the reports available for the form.
        extra_fields (dict): A dictionary containing all the extra hidden input fields found on the form.
        session (requests.Session): The session object used for making HTTP requests.
        url (str): The URL of the form.
        data_frame (pandas.DataFrame): The data frame containing the extracted data.
        xlsfn (str): The name of the Excel file containing the extracted data.
        csvfn (str): The name of the CSV file containing the extracted data.
        check_parameters (bool): A flag indicating whether to check the validity of the parameters.

    Methods:
        __init__(self, mcas_url, check_parameters=True): Initializes the MCASExtract object with the given URL and optional check_parameters flag.
        get_url(self): Returns the URL of the form.
        print_report_options(self): Prints the available report options for the form.
        get_parameters(self): Returns a dictionary of all the available parameters for the form.
        get_report(self, report_name, parameters=None): Retrieves the report with the given report_name and optional parameters.
        process_report(self, report_name, parameters=None): Processes the report with the given report_name and optional parameters.
        download_report(self, report_name, parameters=None): Downloads the report with the given report_name and optional parameters.
        save_data_frame(self, report_name, parameters=None): Saves the data frame containing the extracted data to a CSV file.
        save_excel(self, report_name, parameters=None): Saves the data frame containing the extracted data to an Excel file.
    """
    selects = {}
    reports = {}
    extra_fields = {}
    session = requests.session()
    url = ""
    data_frame = None
    xlsfn = None
    csvfn = None
    check_parameters = True

    def __init__(self, mcas_url, check_parameters=True):
        self.check_parameters = check_parameters

        self.url = mcas_url
        resp = session.get(self.url)
        if resp.status_code != 200:
            raise MCASException(f"Bad http code of {resp.status_code}")
        debug(f"Parsing form at {self.url}")

        bs1 = BeautifulSoup(resp.content, features="html.parser")
        forms = bs1.find_all("form")
        if len(forms) == 0:
            error("Error: Couldn't find any forms at url {}".format(self.url))
            error("Please check the page in a browser.  Here's what the page shows:")
            # system could be down for maintenance, try to see what the page says
            plain_text = bs1.get_text()
            # Clean up the text:
            # 1. Strip leading/trailing whitespace
            cleaned_text = plain_text.strip()
            # 2. Replace multiple newlines with a single newline
            cleaned_text = re.sub(r'\n\s*\n+', '\n\n', cleaned_text)
            # 3. Optionally, remove any extra spaces within the lines
            cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
            print(cleaned_text)
            raise MCASException("Error: couldn't find form at {}".format(self.url))
        try:
            debug('forms is {}'.format(forms[1]))
        except MCASException as e:
            pass

        selects = forms[1].find_all("select")
        # find all the other hidden input fields and include them in the request
        extra_inputs = forms[1].find_all("input")
        for ei in extra_inputs:
            self.extra_fields[ei.attrs['name']] = ei.attrs['value']

        # loop over form data and capture all the different possible select fields
        for s in selects:
            options = s.find_all("option")
            debug(f"select {s.attrs['name']}")
            fieldname = s.attrs['name']
            self.reports[fieldname] = []
            for o in options:
                v = o.attrs['value']
                debug(f"--->  {v}")
                self.reports[fieldname].append(v)
            self.reports['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"

    def set_url(self, inurl):
        self.url = inurl

    def get_report_options(self):
        # at this point, the reports object should contain all values for the various dropdowns
        # debug("report object is: {}".format(reports))
        if self.reports is None:
            print("Error:  Can't find selects information.  Is the URL correct?")
            sys.exit(-1)
        debug(f"Showing all possible options for page {self.url}")
        for x in self.reports:
            debug(f"{x} => {self.reports[x]}")
        return self.reports

    def print_report_options(self):
        # at this point, the reports object should contain all values for the various dropdowns
        # debug("report object is: {}".format(reports))

        if self.reports is None:
            print("Error:  Can't find select boxes information. Is the URL Correct?")
            sys.exit(-1)
        print(f"\n====   Showing ALL possible options for page {self.url}")
        for x in self.reports:
            print(f"request_params['{x}'] = {self.reports[x]}")

        if "-q" in sys.argv:
            sys.exit()

        return self.reports

    def check_report_parameters(self, params):
        # check to see if requested params are in our report
        debug("vals \n{}\n{}".format(sorted(params.keys()), sorted(self.reports.keys())))
        if sorted(params.keys()) != sorted(self.reports.keys()):
            print(" Param Keys: {}")
            for x in sorted(params):
                print("   {}".format(x))
            print(" Required Report Keys:")
            for z in sorted(self.reports):
                print("   {}".format(z))
            raise MCASException("Error: Request and Form do not have same set of keys")

        # Check to see if the requested param values are in our report dictionary
        for z in params:
            if type(params[z]) is list:
                for x in params[z]:
                    if x not in self.reports[z]:
                        raise MCASException("Invalid parameter {} in field {}".format(params[z], z))
            else:
                if params[z] not in self.reports[z]:
                    raise MCASException("Invalid parameter {} in field {}".format(params[z], z))

    def get_report_real(self, parameters):
        """
        Executes a real report request using the given parameters.

        Args:
            parameters (dict): A dictionary of parameters for the report request.

        Returns:
            pandas.DataFrame: The data frame containing the report data.

        Raises:
            MCASException: If the report request parameters are invalid.
            Exception: If the HTTP request fails or the data cannot be decoded.
        """
        reqdict = parameters
        if ('ctl00$ContentPlaceHolder1$hfExport' and 'hfExport') not in reqdict:
            reqdict['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"

        try:
            if self.check_parameters:
                self.check_report_parameters(reqdict)
        except MCASException as e:
            raise MCASException(e)

        for r in reqdict:
            debug("{} = {}".format(r, reqdict[r]))
        final_request = dict()

        # merge all the on-purpose fields and the hidden fields together
        for z in self.extra_fields:
            final_request[z] = self.extra_fields[z]
        # do this second, so it overwrites anything in extra_fields
        for z in reqdict:
            final_request[z] = reqdict[z]

        try:
            res = self.session.post(self.url, final_request)
            if res.status_code != 200:
                raise MCASException("Bad http code of {}".format(res.status_code))
        except MCASException as e:
            debug("Request Error while accessing {} : {}".format(self.url, e))
            quit()

        try:
            debug("request response was {}".format(res))
            debug("data back is: {}".format(res.content))
            excel_data = BytesIO(res.content)

            self.data_frame = pd.read_excel(excel_data, engine='openpyxl')
            return self.data_frame
        except Exception as e:
            print("Fatal Error: Decode of data failed: {}".format(e))

    def get_dataframe(self):
        return self.data_frame

    def set_dataframe(self, df=None):
        if df is not None:
            self.data_frame = df

    def get_url(self):
        return self.url

    # Inserts a column into the data frame at the specified zero-index-based location.
    # All parameters are required
    def add_column(self, location, column_name, column_value):
        if self.data_frame is None:
            raise MCASException("Error: Data Frame not set")

        self.data_frame.insert(loc=location, column=column_name, value=column_value,
                               allow_duplicates=True)

    # Removes the first row of the data frame
    def remove_header_row(self):
        if self.data_frame is None:
            raise MCASException("Error: Data Frame not set")
        self.data_frame = self.data_frame.iloc[1:, :]


    def write_csv(self, csvfilename=None):
        if self.data_frame is None:
            error("Data Frame is not set")
            exit(-1)
        if csvfilename is not None:
            writefn = csvfilename
        else:
            writefn = self.csvfn

        directory = os.path.dirname(writefn)
        if not os.path.exists(directory):
            os.makedirs(directory)

        print("Writing CSV output to {}".format(writefn))
        if os.path.exists(writefn):
            print("WARNING: Overwriting file {}".format(writefn))
        self.data_frame.to_csv(writefn, header=False, index=False)

    @staticmethod
    def map_student_code_to_string(code):
        return student_codes.get(code, "Unknown")


    @staticmethod
    def process_reports(request_params, report, out_directory, sleep_time=10,
                        modify_report_func=None):
        """
        Process reports by looping through all combinations of request parameters,
        fetching reports, and saving them as CSV files.

        Args:
            request_params (dict): A dictionary where keys are parameter names and values are
            lists of possible values.
            report: The report object with methods to manipulate and export data.
            out_directory (str): Directory where CSV files will be saved.
            sleep_time (int): Time to wait between each request (in seconds).
            :param sleep_time:
            :param out_directory:
            :param report:
            :param request_params:
            :param modify_report_func: passed in function to modify the report
        """

        print("\n====  Script will request the following parameters: ")
        for key, values in request_params.items():
            print(f"request_params['{key}'] = {values}")

        # Generate all combinations of parameters using itertools.product
        param_keys = request_params.keys()
        param_values = request_params.values()

        try:
            for combination in itertools.product(*param_values):
                # Build the parameter dictionary dynamically
                param2 = dict(zip(param_keys, combination))

                sleep(sleep_time)  # Throttle requests

                # Print out the parameters being used for this iteration
                print(f"Requesting parameters: {param2}")

                # Call report methods
                report.check_parameters = False
                report.get_report_real(parameters=param2)

                # We always remove the header row, per Matt
                report.remove_header_row()

                # Add necessary columns (assuming the parameter names are part of the column names)
                # for i, key in enumerate(param_keys):
                #     report.add_column(i, key.split('$')[-1], param2[key])

                # Optionally apply the modification function, if provided
                if modify_report_func:
                    modify_report_func(report, param2)

                # Create a CSV filename based on parameter values
                filename = "-".join(map(str, combination)) + ".csv"
                csvfilenamebase = os.path.join(out_directory, filename)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(csvfilenamebase), exist_ok=True)

                # Write the CSV file
                report.write_csv(csvfilenamebase)

        except MCASException as e:
            print(f"MCASExtract Error: {e}")
            exit(-1)


def error(lstr):
    print(lstr)


def log(lstr):
    print(lstr)


def debug(lstr):
    global isDebug

    if isDebug:
        print(lstr)

