import datetime
import itertools
import json
import logging
import mimetypes
import os
import re
import smtplib
import subprocess
import threading
import time
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Iterable, Optional
from pprint import pprint
import bs4 as bs
import numpy as np
import pandas as pd
import requests  # type: ignore
import selenium
import tornado.autoreload
import tornado.ioloop
from selenium.webdriver.chrome.options import Options as chrome_options
from selenium.webdriver.firefox.options import Options as firefox_options

path = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")+ "/"
data_path : str = path + 'data/'
today = datetime.datetime.today()

# logger
dagster_logger = logging.getLogger("dagster_logger")
dagster_logger.setLevel(logging.INFO)
# create console handler
handler = logging.StreamHandler()
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s, %(message)s')
handler.setFormatter(formatter)
# add the handler to the logger
dagster_logger.addHandler(handler)
# create console handler
handler2 = logging.FileHandler(path + "dagster_logger.log")
# add the handler to the logger
dagster_logger.addHandler(handler2)

# BOKEH TOOLS
BOKEH_TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

# Utilities
def set_env(secrets_:dict[str, str]) -> None:
    for x,y in secrets_.items():
        os.environ[str(x)] = str(y)

def convert_large_num_to_human_read(num: int) -> str:
    if num // 10**12 >= 1:
        return f"{(num // 10**12) + (num%10**12)/10**12:,.1f} T"
    elif num // 10**9 >= 1:
        return f"{(num // 10**9) + (num%10**9)/10**9:,.1f} B"
    elif num // 10**6 >= 1:
        return f"{(num // 10**6) + (num%10**6)/10**6:,.1f} M"
    else:
        return f"{int(num):,}"

def write_to_env_file(env_dict: dict[str, Any], file_path, prefix=None):
    """
    Writes the dictionary as environment variables with 'xyz_' prefix into a .env file.

    Parameters:
    - env_dict (dict): Dictionary containing the environment variables.
    - file_path (str): Path where the .env file should be created.

    Example:
    - env_dict = {
        'access_token': 'ccc',
        'api_server': 'https://abc.com/',
        'expires_in': 1800,
        'refresh_token': 'abc',
        'token_type': 'xxx'
    }
    """
    with open(file_path, 'w') as file:
        for key, value in env_dict.items():
            # Add 'xyz_' prefix to the variable names
            env_var_name = key
            if prefix:
                env_var_name = f"{prefix}{key}"
            # Write the variable to the .env file in the format VAR_NAME=VALUE
            file.write(f"{env_var_name}={value}\n")

    print(f".env file created at {file_path}")

def read_json_from_api(url:str, headers:Optional[dict]=None, data:Optional[dict[str, Any]]=None, session: requests.Session = None) -> tuple[Optional[dict], dict[str, Any]]:
    output_data = None
    rate_limit_dict = {"remaining_requests": None, "reset_timestamp_utc": None}
    try:
        if headers:
            if session:
                if data:
                    response = session.get(url, headers=headers, json=data)
                else:
                    response = session.get(url, headers=headers)
            else:
                if data:
                    response = requests.get(url, headers=headers, json=data)
                else:
                    response = requests.get(url, headers=headers)
        else:
            if session:
                if data:
                    response = session.get(url, json=data)
                else:
                    response = session.get(url)

            else:
                if data:
                    response = requests.get(url, json=data)
                else:
                    response = requests.get(url)
        output_data = response.json()
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        if response.headers:
            if response.headers._store:
                if 'x-ratelimit-remaining' in response.headers._store.keys():
                    if response.headers._store['x-ratelimit-remaining']:
                        _, val =  response.headers._store['x-ratelimit-remaining']
                        rate_limit_dict['remaining_requests'] = val
                    if response.headers._store['x-ratelimit-reset']:
                        _, val = response.headers._store['x-ratelimit-reset']
                        rate_limit_dict['reset_timestamp_utc'] = val
    except requests.exceptions.RequestException as e:
        print("Error message:", e)
        if output_data:
            print(f"Failed to make API call.")
            pprint(output_data)
        output_data = {'error': str(e)}
    return output_data, rate_limit_dict

def read_json_from_api_post(url:str, headers:Optional[dict]=None, data:Optional[dict[str, Any]]=None, session: requests.Session = None) -> tuple[Optional[dict], dict[str, Any]]:
    output_data = None
    rate_limit_dict = {"remaining_requests": None, "reset_timestamp_utc": None}
    try:
        if headers:
            if session:
                if data:
                    response = session.post(url, headers=headers, json=data)
                else:
                    response = session.post(url, headers=headers)
            else:
                if data:
                    response = requests.post(url, headers=headers, json=data)
                else:
                    response = requests.post(url, headers=headers)
        else:
            if session:
                if data:
                    response = session.post(url, json=data)
                else:
                    response = session.post(url)

            else:
                if data:
                    response = requests.post(url, json=data)
                else:
                    response = requests.post(url)
        output_data = response.json()
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        if response.headers:
            if response.headers._store:
                if response.headers._store['x-ratelimit-remaining']:
                    _, val =  response.headers._store['x-ratelimit-remaining']
                    rate_limit_dict['remaining_requests'] = val
                if response.headers._store['x-ratelimit-reset']:
                    _, val = response.headers._store['x-ratelimit-reset']
                    rate_limit_dict['reset_timestamp_utc'] = val
    except requests.exceptions.RequestException as e:
        print("Error message:", e)
        if output_data:
            print(f"Failed to make API call.")
            pprint(output_data)
    return output_data, rate_limit_dict

def above_zero_numpy_mask(series):
    # Convert the Pandas Series to a NumPy array for vectorized operations
    array = np.array(series)
    # Create a mask for values greater than 0
    mask = array > 0
    # Apply the vectorization condition to get 1 for values greater than 0 and 0 otherwise
    array[mask] = 1
    array[~mask] = 0
    # Convert the array back to a Pandas Series
    vectorized_series = pd.Series(array.astype(int), index=series.index)
    return vectorized_series

def flatten_list(array: pd.DataFrame | list) -> list:
    if isinstance(array[0], list):
        return [item for sublist in array for item in sublist]
    elif isinstance(array[0], pd.DataFrame):
        return array
    else:
        return array

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    new_iter = list(iterable)  # allows duplicate elements
    return itertools.chain.from_iterable(itertools.combinations(new_iter, r) for r in range(1, len(new_iter) + 1))

def do_work(list_of_tasks:Iterable, wait_time:float=1) -> int:
    """
    This function simulates doing work and returning a number
    :param list_of_tasks: Iterable for a list of tasks to do that take *wait_time* seconds
    :param wait_time: Float or Int for the amount of time the task should take in seconds
    :return: a randomly generated integer between 1 and 10
    """
    for x in list_of_tasks:
        dagster_logger.info(str(x))
        time.sleep(wait_time + np.random.randint(0,10))

    return np.random.randint(0,10)

def find_parent_of_src_folder(start_dir:Optional[str]) -> Optional[str]:
    # Walk upwards through the directory structure
    if start_dir:
        current_path = start_dir
    else:
        current_path = os.getcwd()
    while current_path != os.path.dirname(current_path):  # stop if we reach the root
        if os.path.basename(current_path) == 'src':
            # Return the parent of the 'src' folder
            return os.path.dirname(current_path)
        current_path = os.path.dirname(current_path)  # go up one directory level
    return None  # return None if no 'src' folder is found

def convert_unix_timestamp_to_pandas_date(input_date):
    return pd.to_datetime(datetime.datetime.fromtimestamp(input_date/1000).date())

def parse_date_features(idf_: pd.DataFrame, holidays_: Optional[list] = None) -> pd.DataFrame:
    """
    This function adds several datetime-like features to the input dataframe and returns the dataframe. Optionally, a
    column is made if holiday dates are passed in. This function also creates cyclical hour and month variables.
    :param idf_: an input dataframe for ML that has a datetime index
    :param holidays_: a list of holidays for that region, this parameter is optional
    :return: the dataframe with new datetime-specific columns
    """
    idf = idf_.copy()
    idf.index = pd.to_datetime(idf.index)
    idf["hour"] = idf.index.hour
    idf["month"] = idf.index.month
    idf["year"] = idf.index.year
    idf["weekday"] = idf.index.weekday  # 0 is sunday
    idf["hour_sin"] = np.sin(idf.hour * (2.0 * np.pi / 24))
    idf["hour_cos"] = np.cos(idf.hour * (2.0 * np.pi / 24))
    idf["month_sin"] = np.sin((idf.month - 1) * (2.0 * np.pi / 12))
    idf["month_cos"] = np.cos((idf.month - 1) * (2.0 * np.pi / 12))
    if holidays_:
        idf["holiday"] = [1 if x in holidays_ else 0 for x in idf.index]
    return idf

def wrap_in_paragraphs(txt:str, colour:str="DarkSlateBlue", size:int=4) -> str:
    """
    This function wraps text in paragraph, bold and font tags - according to the colour and size given.
    :param text: text to wrap in tags_
    :param colour: colour of the font
    :param size: size of the font
    :return: string wrapped in html tags
    """
    return f"""<p><b><font color={colour} size={size}>{txt}</font></b></p>"""

def sendemail_(TEXT:str, HTML:str, SUBJECT:str = 'Daily Market Update', filename: Optional[str] = None, TO: Iterable = (os.getenv('my_email'),)):
    """

    This function sends emails to the email list depending on the para

    :param TEXT: text to send in an email
    :param HTML: text to send in an email, but in HTML (default)
    :param SUBJECT: integer that indicates if this is the email sent weekly (start of the week, monday at 7am)
    :param filename: if a file name is present, attach the file to the email and send it
    :return:
    """
    # This is a temporary fix. Be careful of malicious links
    # context = ssl._create_unverified_context()
    TO = list(TO)

    senders_email = os.getenv('senders_email', 'email')  # senders email
    senders_pswd = os.getenv('senders_pw', 'pw')# senders password

    # current date, and a date 5 days away
    curtime = datetime.datetime.now().date()
    # Gmail Sign In
    gmail_sender = senders_email
    gmail_passwd = senders_pswd

    msg = MIMEMultipart('alternative')  # tell the package we'd prefer HTML emails
    msg['Subject'] = SUBJECT  # set the SUBJECT of the email
    msg['From'] = gmail_sender  # set the FROM field of the email
    msg['To'] = ', '.join(TO)  # set the TO field of the email

    # add the 2 parts of the email (one plain text, one html)
    part1 = MIMEText(TEXT, 'plain')
    part2 = MIMEText(HTML, 'html')
    # It will default to the plain text verison if the HTML doesn't work, plain must go first
    msg.attach(part1)
    msg.attach(part2)

    if filename:
        ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        with open(filename) as fp:
            attachment = MIMEText(fp.read(), _subtype=subtype)
        attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(filename))
        msg.attach(attachment)

    # connect to the GMAIL server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    # login to the GMAIL server
    server.login(gmail_sender, gmail_passwd)

    try:
        # send email and confirm email is sent / time it is sent
        server.sendmail(gmail_sender, TO, msg.as_string())
        logging.info(str(curtime) + ' email sent')
    except Exception as e:
        # print error if not sent, and confirm it wasn't sent
        dagster_logger.info(str(e))
        dagster_logger.info(error_handling())
        dagster_logger.info(str(curtime) + ' error sending mail')

    server.quit()

def update_json_file(file_location: str, dictionary: dict) -> None:
    """Updates a JSON file with a dictionary key.

    Args:
        file_location (str): The file path of the JSON file.
        dictionary (dict): The dictionary to update the JSON file with.

    Returns:
        None: The function does not return a value.

    Raises:
        FileNotFoundError: If the JSON file is not found.
        json.JSONDecodeError: If the JSON file has an invalid format.
        Exception: If any other error occurs during the update process.
    """
    try:
        # Load the JSON file
        with open(file_location, 'r') as file:
            data = json.load(file)

        # Update the JSON data with the dictionary
        data.update(dictionary)

        # Write the updated data back to the JSON file
        with open(file_location, 'w') as file:
            json.dump(data, file, indent=4)

        dagster_logger.info("JSON file updated successfully.")
    except FileNotFoundError:
        dagster_logger.info("File not found.")
    except json.JSONDecodeError:
        dagster_logger.info("Invalid JSON file format.")
    except Exception as e:
        dagster_logger.info(f"An error occurred: {str(e)}")

def error_handling() -> str:
    """
    This function returns a string with all of the information regarding the error
    :return: string with the error information
    """
    return traceback.format_exc()

# Selenium / Chrome-related
def get_chromedriver_download_table():
    url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    response = read_json_from_api(url)
    ok = []
    for ver in response['versions']:
        try:
            for w in ver['downloads']['chromedriver']:
                ok.append({"revision": ver['revision'], 'version': ver['version'], 'platform': w['platform'], 'url':w['url']})
        except KeyError:
            pass
    wow = pd.DataFrame(ok)
    wow['timestamp'] = response['timestamp']
    return wow

def check_selenium_browser_driver_ubuntu(path_to_chromedriver_dir):
    version = get_application_version_ubuntu()
    vers = version.split('.')[0]
    assert f"chromedriver{vers}" in os.listdir(path_to_chromedriver_dir + "chromedriver/")[0], f"in_folder= {os.listdir(path_to_chromedriver_dir + "chromedriver/")}, path= {path_to_chromedriver_dir}, version= {vers}, chromedriver{vers}.exe not in chromedriver folder"
    dagster_logger.info(f"ChromeDriver version and Browser version are synced {vers}")

def get_application_version_ubuntu(path_to_exe=r"google-chrome"):
    command = rf"""{path_to_exe} --version"""
    version = ''.join([b for b in os.popen(command).readlines()])
    version = re.findall(r"\s(\d+.+)", version, )[0].strip()
    return version

def get_selenium_driver(browser="chrome", dat_path='/home/jay/PycharmProjects/home/data/'):
    if browser == 'chrome':
        vers = get_application_version_ubuntu().split('.')[0]
        chromeOptions = chrome_options()
        chromeOptions.binary_location = '/usr/bin/google-chrome'
        chromeOptions.add_experimental_option("prefs", {
            "download.default_directory": r"/home/jay/Downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--disable-dev-shm-usage')
        # chrome_driver_path = dat_path + 'chromedriver/chromedriver' + vers
        driver = selenium.webdriver.Chrome(options=chromeOptions)
    else:
        firefoxOptions = firefox_options()
        firefoxOptions.set_preference("browser.download.folderList", 2)
        firefoxOptions.set_preference("browser.download.manager.showWhenStarting", False)
        firefoxOptions.set_preference("browser.download.dir", path.replace('/', '\\') + 'data\\downloads\\')
        firefoxOptions.set_preference("browser.helperApps.neverAsk.saveToDisk",
                                      "application/octet-stream,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        driver = selenium.webdriver.Firefox(options=firefoxOptions)
    return driver

def grab_soup(url_, driver):
    """
    This function enables a driver (using Firefox or Chrome), goes to the URL, and retrieves the data after the JS is loaded.

    :param url_: url to go to to retrieve data
    :param browser: browser to use, defaults to firefox (requires geckodriver.exe on path)
    :return:

    soup - the data of the page
    driver - the browser (process) instance
    """
    driver.get(url_)  # go to the URL
    _ = driver.page_source
    time.sleep(1)  # sleep for 1 second  to ensure all JS scripts are loaded
    html = driver.execute_script("return document.body.outerHTML;")  # execute javascript code
    soup_ = bs.BeautifulSoup(html, 'lxml')  # read the data as html (using lxml driver)
    return soup_

def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


# BOKEH
def run_bokeh_app(files, port=5002, new='tab'):
    # all files in directory that you want as bokeh apps
    # run_bokeh_app(["finance_charts.py",])
    # run_bokeh_app(["personal.py", ])

    def create_bokeh_server(io_loop, files, argvs, host, port):
        '''Start bokeh server with applications paths'''
        from bokeh.command.util import build_single_handler_applications
        from bokeh.server.server import Server

        # Turn file paths into bokeh apps
        apps = build_single_handler_applications(files, argvs)

        # kwargs lifted from bokeh serve call to Server, with created io_loop
        kwargs = {
            'io_loop': io_loop,
            'generate_session_ids': True,
            'redirect_root': True,
            'use_x_headers': False,
            'secret_key': None,
            'num_procs': 1,
            'host': host,
            'sign_sessions': False,
            'develop': False,
            'port': port,
            'use_index': True
        }
        server = Server(apps, **kwargs)

        return server

    def start_bokeh(io_loop):
        '''Start the `io_loop`'''
        io_loop.start()
        return None

    def launch_app(host, app_name, new):
        '''Lauch app in browser

        Ideally this would `bokeh.util.browser.view()`, but it doesn't work
        '''
        import webbrowser

        # Map method strings to webbrowser method
        options = {'current':0, 'window':1, 'tab':2}

        # Concatenate url and open in browser, creating a session
        app_url = 'http://{}/{}'.format(host, app_name)
        print('Opening `{}` in browser'.format(app_url))
        webbrowser.open(app_url, new=options[new])

        return None

    def server_loop(server, io_loop):
        '''Check connections once session created and close on disconnect'''
        import time

        connected = [True,]
        session_loaded = False
        while any(connected):

            # Check if no session started on server
            sessions = server.get_sessions()
            if not session_loaded:
                if sessions:
                    session_loaded = True
            # Once 1+ sessions started, check for no connections
            else:
                # List of bools for each session
                connected = [True,]*len(sessions)
                # Set `connected` item false no connections on session
                for i in range(len(sessions)):
                    if sessions[i].connection_count == 0:
                        connected[i] = False
            # Keep the pace down
            time.sleep(2)

        # Stop server once opened session connections closed
        io_loop.stop()

        return None



    # Initialize some values, sanatize the paths to the bokeh plots
    argvs = {}
    app_names = []
    for path in files:
        argvs[path] = None
        app_names.append(os.path.splitext(os.path.split(path)[1])[0])

    # Concate hostname/port for creating handlers, launching apps
    host = 'localhost:{}'.format(port)
    # Initialize the tornado server
    io_loop = tornado.ioloop.IOLoop.instance()
    # tornado.autoreload.start(io_loop)

    # Add the io_loop to the bokeh server
    server = create_bokeh_server(io_loop, files, argvs, host, port)

    print('Starting the server on {}'.format(host))
    args = (io_loop,)
    th_startup = threading.Thread(target=start_bokeh, args=args)
    th_startup.start()

    # Launch each application in own tab or window
    th_launch = [None,]*len(app_names)
    for i in range(len(app_names)):
        args = (host, app_names[i], new)
        th_launch[i] = threading.Thread(target=launch_app, args=args)
        th_launch[i].start()
        # Delay to allow tabs to open in same browser window
        time.sleep(2)

    # Run session connection test, then stop `io_loop`
    args = (server, io_loop)
    th_shutdown = threading.Thread(target=server_loop, args=args)
    th_shutdown.start()

# DATE HELPERS
def split_date_range_into_months(start_date: pd.Timestamp, end_date: pd.Timestamp) -> list[tuple[str,str]]:
    """Splits the range from start_date to end_date into monthly ranges."""
    months = []
    current_start = start_date.replace(day=1)

    while current_start <= end_date:
        # Get the last day of the current month
        current_end = (current_start + pd.offsets.MonthEnd(0)).date()  # Last day of the current month

        # Ensure we do not exceed the overall end_date
        current_end = min(current_end, end_date.date())

        # Append the current month's range as a tuple
        months.append((current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d')))

        # Move to the next month
        current_start = (current_start + pd.DateOffset(months=1)).replace(day=1)

    return months

def convert_column_name(column_name: str) -> str:
    """
    Converts a camelCase or PascalCase string into snake_case.

    Args:
    - column_name (str): The input column name in camelCase or PascalCase.

    Returns:
    - str: The column name converted to snake_case.
    """
    # Use regular expression to add underscores before capital letters and convert them to lowercase
    result = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', column_name).lower()
    result = result.replace(" ", "_")
    return result.strip()

def is_business_day(date: datetime.date) -> bool:
    return bool(len(pd.bdate_range(date, date)))

def date_conversion(date: str | datetime.datetime | None, return_type: str = 'str'):
    if date is None:
        return None
    elif isinstance(date, str):
        try:
            date_obj = datetime.datetime.fromisoformat(date)
        except ValueError:
            raise ValueError(f"Invalid date string format: {date}. Expected ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).")
    elif isinstance(date, datetime.datetime):
        date_obj = date
    else:
        raise TypeError(f"Unsupported date type: {type(date)}")

    if return_type == "str":
        return date_obj.isoformat()
    elif return_type == "short":
        return date_obj.strftime("%Y-%m-%d")
    elif return_type == "obj":
        return date_obj
    elif return_type == "timestamp":
        return pd.to_datetime(date_obj)
    else:
        raise ValueError(f"Invalid return_type: {return_type}. Expected 'str' or 'datetime'.")


# WINDOWS FUNCS
def get_application_version_windows(
        path_to_exe=r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"):
    command = rf""" wmic datafile where name="{path_to_exe}" get Version /value """
    version = ''.join([b for b in os.popen(command).readlines()])
    version = version.strip().split('=')[1]
    return version

def execute_cmd_windows(commands: str) -> Optional[str]:
    try:
        out_var = subprocess.Popen(commands, shell=True)
        dagster_logger.info(f"{commands} | Running...")

        (output, err) = out_var.communicate()
        output_str = None
        err_str = None
        # Decode the output and error from bytes to string
        # Print the output and error
        if output:
            output_str = output.decode('utf-8')
            print("Output:")
            # This will give you the output of the command being executed
            dagster_logger.info("Command output: " + output_str)

        if err:
            err_str = err.decode('utf-8')
            print("Error:")
            print(err_str)

        return output_str
    except Exception:
        dagster_logger.info(error_handling())
        return "Did not run"

def check_selenium_browser_driver_windows():
    version = get_application_version_windows()
    assert f"chromedriver{version.split('.')[0]}.exe" in os.listdir(data_path + "chromedriver/"), f"version = {version}, chromedriver{version.split('.')[0]}.exe not in chromedriver folder"
    dagster_logger.info(f"ChromeDriver version and Browser version are synced {version}")