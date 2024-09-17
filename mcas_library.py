


#
# Massachusetts MCAS data extractor - will download data from the Massachusetts MCAS site
# and format it to .xlsx and .csv files in an output directory
#
# Created by Kurt Overberg for Boston Schools Fund
# (C) 2022 Xrtic Consulting
#
# Libraries needed for this script:
#
# beautifulsoup4==4.10.0
# certifi==2021.10.8
# charset-normalizer==2.0.12
# et-xmlfile==1.1.0
# idna==3.3
# numpy==1.22.3
# openpyxl==3.0.9
# pandas==1.4.1
# python-dateutil==2.8.2
# pytz==2022.1
# requests==2.27.1
# six==1.16.0
# soupsieve==2.3.1
# urllib3==1.26.9
# xlrd==2.0.1

import os.path
import requests
import pandas as pd
from bs4 import BeautifulSoup
from os.path import join, isdir, abspath, pathsep
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from io import BytesIO

import sys


report_type = 'DISTRICT'
year = '2018'
grade = 'AL'
school_type = 'ALL'
sub_group = 'AL:AL'
output_directory = './'
isDebug = False

report_url = "https://profiles.doe.mass.edu/statereport/mcas.aspx"
extra_fields = dict()
session = requests.session()
list_options = False
reports = dict()


class MCASException(Exception):
    pass


class MCASExtract:
    selects = dict()
    reports = dict()
    extra_fields = dict()
    session = requests.session()
    # url = "https://profiles.doe.mass.edu/statereport/mcas.aspx"
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
            raise Exception("Bad http code of {}".format(resp.status_code))
        debug("Parsing form at {}".format(self.url))

        bs1 = BeautifulSoup(resp.content, features="html.parser")
        forms = bs1.find_all("form")

        debug("forms is {}".format(forms[1]))

        selects = forms[1].find_all("select")
        # find all the other hidden input fields and include them in the request
        extra_inputs = forms[1].find_all("input")
        for ei in extra_inputs:
            self.extra_fields[ei.attrs['name']] = ei.attrs['value']

        # loop over form data and capture all the different possible select fields
        for s in selects:
            options = s.find_all("option")
            debug("select {}".format(s.attrs['name']))
            fieldname = s.attrs['name']
            self.reports[fieldname] = list()
            for o in options:
                v = o.attrs['value']
                debug("--->  {}".format(v))
                self.reports[fieldname].append(v)
            self.reports['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"

    def set_url(self, inurl):
        self.url = inurl

    def get_report_options(self):
        # at this point, the reports object should contain all values for the various dropdowns
        # debug("report object is: {}".format(reports))
        if self.reports is None:
            print("Error:  Can't find selects information.  Is the URL correct?")
            exit(-1)
        debug("Showing possible options for page {}".format(self.url))
        for x in self.reports:
            debug("{} => {}".format(x, self.reports[x]))
        return self.reports

    def print_report_options(self):
        # at this point, the reports object should contain all values for the various dropdowns
        # debug("report object is: {}".format(reports))

        if self.reports is None:
            print("Error:  Can't find select boxes information. Is the URL Correct?")
            exit(-1)
        print("Showing possible options for page {}".format(self.url))
        for x in self.reports:
            print("request_params['{}'] = {}".format(x, self.reports[x]))

        if "-d" in sys.argv:
            quit()

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
            if type(params[z]) == list:
                for x in params[z]:
                    if x not in self.reports[z]:
                        raise MCASException("Invalid parameter {} in field {}".format(params[z], z))
            else:
                if params[z] not in self.reports[z]:
                    raise MCASException("Invalid parameter {} in field {}".format(params[z], z))

    def get_report(self, parameters):

        param2 = dict()
        for a in parameters['ctl00$ContentPlaceHolder1$ddReportType']:
            for b in parameters['ctl00$ContentPlaceHolder1$ddYear']:
                for c in parameters['ctl00$ContentPlaceHolder1$ddGrade']:
                    for d in parameters['ctl00$ContentPlaceHolder1$ddSchoolType']:
                        for e in parameters['ctl00$ContentPlaceHolder1$ddSubGroup']:
                            param2['ctl00$ContentPlaceHolder1$ddReportType'] = a
                            param2['ctl00$ContentPlaceHolder1$ddYear'] = b
                            param2['ctl00$ContentPlaceHolder1$ddGrade'] = c
                            param2['ctl00$ContentPlaceHolder1$ddSchoolType'] = d
                            param2['ctl00$ContentPlaceHolder1$ddSubGroup'] = e
                            param2['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"

                            self.get_report_real(parameters=param2)
                            # now add a year column
                            # rpt.add_column(0, 'Year', '2001')
                            # filenamebase = "{}-{}-{}-{}-{}.csv".format(a, b, c, d, e)
                            # rpt.write_csv(filenamebase)

    def get_report_real(self, parameters):
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
        # debug("Requesting:{}".format(reqdict))
        final_request = dict()

        # merge all the on-purpose fields and the hidden fields together
        for z in self.extra_fields:
            final_request[z] = self.extra_fields[z]
        # do this second so it overwrites anything in extra_fields
        for z in reqdict:
            final_request[z] = reqdict[z]

        # print("Final_request is {}".format(final_request))
        # for i in final_request:
        #     print("arr[{}] = {}".format(i, final_request[i]))
        try:
            res = self.session.post(self.url, final_request)
            if res.status_code != 200:
                raise Exception("Bad http code of {}".format(res.status_code))
        except Exception as e:
            debug("Request Error while accessing {} : {}".format(self.url, e))
            quit()

        try:
            debug("request response was {}".format(res))
            debug("data back is: {}".format(res.content))
            # tfile1 = open("content_dump.html", "wb")
            # tfile1.write(res.content)
            # tfile1.close()

            # self.data_frame = pd.read_csv(res.content)
            # self.data_frame = pd.read_csv(res.content, engine='xlrd')

            # wb = load_workbook(filename=BytesIO(res.content))
            # wb.active = 0
            # ws = wb[0]
            # self.data_frame = pd.DataFrame(ws.values)
            excel_data = BytesIO(res.content)

            self.data_frame = pd.read_excel(excel_data, engine='openpyxl')
            # any processing of data (adding columns, etc) goes here.
            # Here we chop off the first (header) row
            # before saving as a CSV for later concatenation
            # df = self.data_frame.iloc[1:, :]
            # now add a year column
            # self.data_frame.insert(loc=0, column='Year', value=year, allow_duplicates=True)
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

    def set_url(self, theurl):
        self.url = theurl

    # Inserts a column into the data frame at the specified zero-index-based location.
    # All parameters are required
    def add_column(self, location, column_name, column_value):
        if self.data_frame is None:
            raise Exception("Error: Data Frame not set")

        self.data_frame.insert(loc=location, column=column_name, value=column_value, allow_duplicates=True)

    # Removes the first row of the data frame
    def remove_header_row(self):
        if self.data_frame is None:
            raise MCASException("Error: Data Frame not set")
        self.data_frame = self.data_frame.iloc[1:, :]

    def write_xlsx(self, xlsxfilename=None):
        wb = Workbook()
        ws = wb.active


        for r in dataframe_to_rows(self.data_frame, index=True, header=True):
            ws.append(r)

        if os.path.exists(xlsxfilename):
            print("WARNING: Overwriting file {}".format(xlsxfilename))
        wb.save(xlsxfilename)

    def write_csv(self, csvfilename=None):
        writefn = ''
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



def error(lstr):
    print(lstr)

def log(lstr):
    print(lstr)


def debug(lstr):
    global isDebug

    if isDebug:
        print(lstr)


# Init function will go get the specified page and parse it for various form select values it contains
# and put them into the "reports" global, which is a dict with form names as the key and possible values as
# a list...so:
# reports['ctl00$ContentPlaceHolder1$ddYear'] = ['2021', '2020', '2019'...]
# ...where the values are read from the form.  This is helpful in knowing what the possible values are
# for any given URL.  You have to always call init() before doing anything else in the main part of the script,
# as it sets up a number of variables (& cookies, etc) that are needed to get the reports.
def init():
    global reports, session
    resp = session.get(report_url)
    if resp.status_code != 200:
        raise Exception("Bad http code of {}".format(resp.status_code))
    debug("Parsing form at {}".format(report_url))
    # print("resp is {}".format(resp.content))
    # with open(filename, mode='wb') as localfile:
    #     localfile.write(resp.content)

    bs1 = BeautifulSoup(resp.content, features="html.parser")
    forms = bs1.find_all("form")

    debug("forms is {}".format(forms[1]))

    selects = forms[1].find_all("select")
    # find all the other hidden input fields and include them in the request
    extra_inputs = forms[1].find_all("input")
    for ei in extra_inputs:
        extra_fields[ei.attrs['name']] = ei.attrs['value']

    # loop over form data and capture all the different possible select fields
    for s in selects:
        options = s.find_all("option")
        debug("select {}".format(s.attrs['name']))
        fieldname = s.attrs['name']
        reports[fieldname] = list()
        for o in options:
            v = o.attrs['value']
            debug("--->  {}".format(v))
            reports[fieldname].append(v)

    # at this point, the reports object should contain all values for the various dropdowns
    # debug("report object is: {}".format(reports))
    if list_options:
        print("Showing possible options for page {}".format(report_url))
        for x in reports:
            print("{} => {}".format(x, reports[x]))

        exit()
    debug("now formulating request to {}".format(report_url))


# perform the get
def get_mcas_data(url, output_directory='./', report_type='DISTRICT',
                  year='2018', grade='AL', school_type='ALL', sub_group='AL:AL'):
    global report_url, session
    res = None
    reqdict = dict()
    reqdict['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"
    # extra_fields will overwrite the report

    # report type one of DISTRICT, SCHOOL, COLLABORATIVE
    reqdict['ctl00$ContentPlaceHolder1$ddReportType'] = report_type

    # report year
    reqdict['ctl00$ContentPlaceHolder1$ddYear'] = year

    # Grade - AL, 03, 04, 05, 06, 07, 08, 10, HS
    reqdict['ctl00$ContentPlaceHolder1$ddGrade'] = grade

    # SchoolType: ALL, Elementary School, Elementary - Middle School,
    #             Middle School,  Middle - High School or K - 12, High School
    reqdict['ctl00$ContentPlaceHolder1$ddSchoolType'] = school_type

    # sub groups - AL:AL, ED:N, ED:Y, FL:N, FL:Y, GE:01, GE:02, HN:Y, MG:Y, MH:Y, RA1:01, RA1:02, RA1:03, RA1:04,
    #              RA1:06, RA1:15, RA1:20, SS:FLEP, SS:LEP, SS:LEPFLEP, SS:everELL, SS:SPED, T1:0,
    #              T1:1, SS:Non-SPED, FT:Y, HL:Y, MT:Y
    reqdict['ctl00$ContentPlaceHolder1$ddSubGroup'] = sub_group
    reqdict['ctl00$ContentPlaceHolder1$hfExport'] = "Excel"
    for r in reqdict:
        debug("{} = {}".format(r, reqdict[r]))
    # debug("Requesting:{}".format(reqdict))
    final_request = dict()

    # merge all the on-purpose fields and the hidden fields together
    for z in extra_fields:
        final_request[z] = extra_fields[z]
    for z in reqdict:
        final_request[z] = reqdict[z]

    # make sure there's a slash on the end
    output_directory = abspath(output_directory)
    filenamebase = "{}-{}-{}-{}-{}".format(report_type, year, grade, school_type, sub_group)
    filenamebase = os.path.join(output_directory, filenamebase)
    xlsfile = "{}.xlsx".format(filenamebase).replace(" ", "_")
    csvfile = "{}.csv".format(filenamebase).replace(" ", "_")
    try:
        res = session.post(url, final_request)
        if res.status_code != 200:
            raise Exception("Bad http code of {}".format(res.status_code))
    except Exception as e:
        debug("Request Error while accessing {} : {}".format(url, e))
        quit()

    try:
        debug("request response was {}".format(res))
        excel_file = BytesIO(res.content)

        # Use read_excel with the BytesIO object
        df = pd.read_excel(excel_file)
        # log("Data Preview:\n {}".format(df))

        # any processing of data (adding columns, etc) goes here.
        # Here we chop off the first (header) row
        # before saving as a CSV for later concatenation
        df = df.iloc[1:, :]
        # now add a year column
        df.insert(loc=0, column='Year', value=year, allow_duplicates=True)
        # output data to .xlsx and .csv files
        log("Outputting {}".format(xlsfile))
        log("Outputting {}".format(csvfile))
        # with open(xlsfile, mode='wb') as localfile:
        #     localfile.write(res.content)
        # with open(xlsfile, mode='wb') as localfile:
        #     localfile.write(exceldata)
        # df.to_excel(xlsfile)
        df.to_excel(xlsfile)
        df.to_csv(csvfile, index=False, header=False)

    except Exception as e:
        print("Fatal Error: Decode of data failed: {}".format(e))


