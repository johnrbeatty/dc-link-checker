import pandas as pd
import requests
import random
import time

from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def get_metadata(input_file, verbose, buy_link_check=False):
    # Open an Excel file and check to make sure it's actually a content inventory spreadsheet from Digital Commons.
    # All of these fields should be present in any Digital Commons content inventory spreadsheet. There are only
    # two necessary fields. The first is wf_areyouuploadingaf1, which should be "wf_yes" for any publication that has
    # full text uploaded and should be "wf_no" for
    # any publication that has a link out. It should be empty for metadata-only records.
    # The other is download_url, which contains the URLs that are to be checked.
    # Everything else is included to assist the user in tracking down any problem links.
    # If there are no book galleries in the repository, then there will be no buy_link field.
    # So the existence of that field needs to be checked before it is selected.

    xl = pd.ExcelFile(input_file)
    if xl.sheet_names[0] == "Content Inventory":
        inventory = xl.parse("Content Inventory")
        if "buy_link" in inventory.columns.values.tolist():
            fields = ["title", "state", "submission_date", "wf_areyouuploadingaf1", "context_key", "front_end_url",
                      "download_url", "buy_link", "manuscript_id"]
        else:
            fields = ["title", "state", "submission_date", "wf_areyouuploadingaf1", "context_key", "front_end_url",
                      "download_url", "manuscript_id"]
            if buy_link_check is True:
                print("No buy links present")
        inventory = inventory[fields]
        inventory = inventory[inventory["state"] == "published"]
        if buy_link_check is False:
            inventory = inventory[inventory["wf_areyouuploadingaf1"] == "wf_no"]
            inventory = inventory[inventory["download_url"].str.len() > 0]
        else:
            inventory = inventory[inventory["buy_link"].str.len() > 0]
        if verbose:
            print(f"Found {len(inventory)} links")
        return inventory
    else:
        print("File does not appear to be a valid Digital Commons Content Inventory spreadsheet")
    # FIXME: I probably need to raise an error here so that execution is halted before any further procedures are called


def links_list(input_table, buy_link_check=False):
    if buy_link_check is False:
        link_field = "download_url"
    else:
        link_field = "buy_link"
    links = input_table[link_field].tolist()
    return links


def check_links(link_list, verbose, timeout):
    # FIXME: Implement Javascript for Cloudflare check to avoid 403 errors? Or just leave?

    headers = {
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    response_list = []

    for i in range(len(link_list)):
        session = requests.Session()
        session.headers.update(headers)
        try:
            if verbose:
                print(f"Trying row {i}, {link_list[i]}: ", end="")
            response = session.get(link_list[i], timeout=timeout)
            status_code = response.status_code
            if status_code == 429:
                delay = random.randint(30, 60)
                print(f"Too many requests. Waiting {delay} seconds to retry.")
                time.sleep(delay)
                status_code = response.status_code
            if verbose:
                print(status_code)
            response_list.append(status_code)
            # print(response.headers)
            if i < len(link_list)-1:
                this_url = urlparse(link_list[i])
                next_url = urlparse(link_list[i+1])
                if this_url.hostname == next_url.hostname:
                    delay = random.randint(10, 30)
                    print(f"Waiting for {delay} seconds.")
                    time.sleep(delay)
        except IndexError:
            print("Index error. Moving on. Someone should fix the code.")
        except requests.exceptions.Timeout as err:
            print(f"Error: {err=}, {type(err)=}, Link {link_list[i]}")
            response_list.append("Timeout")
        except requests.exceptions.TooManyRedirects as err:
            print(f"Error: {err=}, {type(err)=}, Link {link_list[i]}")
            response_list.append("Too Many Redirects")
        except requests.exceptions.ConnectionError as err:
            print(f"Connection Error in Link {link_list[i]}: {err=}")
            response_list.append("Connection Error-Check URL")
        except Exception as err:
            print(f"Error: {err=}, {type(err)=}, Link {link_list[i]}")
            response_list.append("Error-check output")
    return response_list


def write_response_spreadsheet(filename, input_table):
    wb = Workbook()
    ws = wb.active
    ws.title = "Links"

    # FIXME: Is there a way to not add the blank line after the headers?
    for r in dataframe_to_rows(input_table, header=True):
        ws.append(r)
    try:
        wb.save(filename)
    except FileNotFoundError:
        print("Invalid path or filename. Saving as checked_links.xlsx in current directory.")
        wb.save("checked_links.xlsx")


def check_all_links(input_file, output_file, verbose, buy_links, timeout=10):
    # FIXME: Add an option to start processing at a specific line number?
    # FIXME: This will only work if there is an option to only save the links list before it is processed.

    metadata_table = get_metadata(input_file, verbose, buy_links)
    link_list = links_list(metadata_table, buy_links)
    response_list = check_links(link_list, verbose, timeout)
    metadata_table.insert(len(metadata_table.columns), "response", response_list)
    write_response_spreadsheet(output_file, metadata_table)
