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
import sys, getopt
from bs4 import BeautifulSoup
from os.path import join, isdir, abspath, pathsep

report_type = 'DISTRICT'
year = '2018'
grade = 'AL'
school_type = 'ALL'
sub_group = 'AL:AL'
output_directory = './'
isDebug = False

report_url = "https://profiles.doe.mass.edu/statereport/mcas.aspx"
filename = "stateoutput.html"
outputfile = "reqoutput.xls"
extra_fields = dict()
session = requests.session()
list_options = False
reports = dict()


def log(lstr):
    print(lstr)


def debug(lstr):
    global isDebug

    if isDebug:
        print(lstr)


def print_usage():
    print('')
    print('extract.py [options]')
    print('')
    print('        -h, --help               -  Show this page')
    print('')
    print('        -l, --list_options       - Reads the webpage listed in --url and dumps out all values ')
    print('                                   for dropdown values, then exits.')
    print('')
    print('         -d                      - Debug mode (detailed output)')
    print('')
    print('        --url="<page URL>"       - Will read and submit to the specified URL')
    print('')
    print('        --output=<directory>     - Will output .xlsx and .csv files into specified directory')
    print('')
    print('        --report_type="<type>"   - [DISTRICT|SCHOOL|COLLABORATIVE]')
    print('')
    print('        --year="<year>"          - Depending on URL, values range from 1997-2021')
    print('')
    print('        --grade="<grade>"        - [AL|03|04|05|06|07|08|10|HS]')
    print('')
    print('        --school_type="<type>"   - [ALL, Elementary School, Elementary - Middle School,')
    print('                                    Middle School,  Middle - High School or K - 12, High School]')
    print('')
    print('        --sub_group="<subgroup>" - [AL:AL, ED:N, ED:Y, FL:N, FL:Y, GE:01, GE:02, HN:Y, ')
    print('                                    MG:Y, MH:Y, RA1:01, RA1:02, RA1:03, RA1:04, RA1:06')
    print('                                    RA1:15, RA1:20, SS:FLEP, SS:LEP, SS:LEPFLEP, SS:everELL, SS:SPED,')
    print('                                    T1:0, T1:1, SS:Non-SPED, FT:Y, HL:Y, MT:Y]')
    print('                                    ...or others depending on url')
    print('')
    print('')


# parse the command line options and set global flags
# https://www.tutorialspoint.com/argument-parsing-in-python
def parse_options(argv):
    # specify which globals get set by options
    global report_type, year, grade, school_type, sub_group, output_directory
    global list_options, report_url, isDebug
    try:
        opts, args = getopt.getopt(argv,
                                   "hvrlt:y:g:st:sg:o:u:",
                                   ["report_type=", "year=", "grade=",
                                    "school_type=", "sub_group=", "output=",
                                    "url="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-rt", "--report_type"):
            report_type = arg
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-g", "--grade"):
            grade = arg
        elif opt in ("-st", "--school_type"):
            school_type = arg
        elif opt in ("-sg", "--sub_group"):
            sub_group = arg
        elif opt in ("-o", "--output"):
            output_directory = arg
        elif opt in ("-u", "--url"):
            report_url = arg
        elif opt in "-l":
            list_options = True
        elif opt in "-v":
            isDebug = True


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
        df = pd.read_excel(res.content)
        log("Data Preview:\n {}".format(df))

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


def get_single(argv):
    init()
    get_mcas_data(report_url, output_directory, report_type, year, grade, school_type, sub_group)


def get_year(year):
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



def main(argv):
    parse_options(argv)
    get_single(argv)
    # get_year("2018")


if __name__ == "__main__":
    main(sys.argv[1:])
