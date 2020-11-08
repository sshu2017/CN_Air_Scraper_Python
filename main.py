import json
import csv
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def generate_city() -> dict:
    """Find all cities on the main page"""
    main_page = requests.get("http://pm25.in/")
    main_soup = BeautifulSoup(main_page.content, 'html.parser')
    cities = main_soup.select(".unstyled > div > li > a")
    return dict(zip([city.text for city in cities],
                    [city.get('href') for city in cities]))


def format_one_table(input_table) -> list:
    """Turn a table on one page into a list of dictionaries"""
    rows = input_table.findAll("tr")
    header_row = [th.text for th in rows[0].select("th")]

    table_as_list = [] # list of dicts
    for r in range(1, len(rows)):
        row = [td.text for td in rows[r].select("td")]
        row_dict = dict(zip(header_row, row))
        table_as_list.append(row_dict)

    return table_as_list


def get_one_city(city_name: str, city_url: str) -> tuple:
    city_url = "http://pm25.in" + city_url
    city_page = requests.get(city_url)
    city_soup = BeautifulSoup(city_page.content, 'html.parser')
    time_stamp = city_soup.findAll("div", {"class": "live_data_time"})[0].select("p")[0].text
    concentration_unit = city_soup.findAll("div", {"class": "live_data_unit"})[0].text.strip()

    city_data = city_soup.select("#detail-data")
    city_data_formatted = format_one_table(city_data[0])

    return time_stamp, concentration_unit, city_data_formatted


def save_one_city_results(time_stamp: str,
                          concentration_unit: str,
                          city_data_formatted: list,
                          city_name: str) -> str:

    dict_output = {"city": city_name,
                   "time_stamp": time_stamp,
                   "unit": concentration_unit,
                   "data": city_data_formatted}

    # https://stackoverflow.com/a/18337754/3768495
    str_output = json.dumps(dict_output, ensure_ascii=False)
    return str_output


def generate_outfile_name():
    current_year_month = datetime.strftime(datetime.now(), "%Y-%m")
    return "output/data_" + current_year_month + ".csv"


def main():
    cities = generate_city()
    output_file = generate_outfile_name()

    with open(output_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        csvwriter = csv.writer(csvfile,
                               quoting=csv.QUOTE_NONE,
                               escapechar='\\')
        for name, url in cities.items():
            time.sleep(1)
            str_out = save_one_city_results(*get_one_city(name, url), name)
            csvwriter.writerow([str_out])


if __name__ == '__main__':
    main()
