import pandas as pd
import mechanicalsoup
import logging


def get_experimental_ionization_energy(formula, url="https://cccbdb.nist.gov/xp1x.asp?prop=8"):
    """
    Fetches experimental ionization energy data for a given chemical formula from a specified URL.

    Args:
    - formula: Chemical formula
    - url: URL to fetch the ionization energy data (default: CCCBDB URL)

    Returns:
    - DataFrame containing ionization energy data
    """
    browser = mechanicalsoup.Browser()

    logging.basicConfig(filename='error.log', level=logging.ERROR)

    try:
        login_page = browser.get(url)
        login_html = login_page.soup
        
        form = login_html.select("form")[0]
        form.select("input")[0]["value"] = formula

        profiles_page = browser.submit(form, login_page.url)
        l_page = browser.get(profiles_page.url)
        l_html = l_page.soup

        try:
            new_form = l_html.select("form")[1]
            final_page = browser.submit(new_form, l_page.url)
            html_table = final_page.soup.findAll('table')[1]
        except IndexError:
            html_table = profiles_page.soup.findAll('table')[1]

        list_table = table_data_text(html_table)
        dftable = pd.DataFrame(list_table)

        return dftable

    except Exception as e:
        error_message = f"Error processing {formula}: {e}"
        print(error_message)
        logging.error(error_message)
        return None  


def table_data_text(table):
    """
    Parses an HTML segment starting with the <table> tag followed by multiple <tr> (table rows)
    and inner <td> (table data) tags. It returns a list of rows with inner columns.
    Accepts only one <th> (table header/data) in the first row.
    """
    logger = logging.getLogger(__name__)

    def row_get_data_text(tr, col_tag='td'):
        return [td.get_text(strip=True) for td in tr.find_all(col_tag)]

    rows = []
    try:
        trs = table.find_all('tr')
        header_row = row_get_data_text(trs[0], 'th')

        if header_row:
            rows.append(header_row)
            trs = trs[1:]

        for tr in trs:
            rows.append(row_get_data_text(tr, 'td'))

    except (AttributeError, IndexError) as e:
        logger.error(f"Error processing table data: {e}")
        rows = []

    return rows


def get_hform_data(formula, url="https://cccbdb.nist.gov/xp1x.asp", data_directory="/data_directory/"):
    
    """
    This function retrieves experimental enthalpy of formation data in kJ/mol at both a reference temperature and at 0K from
    the Computational Chemistry Comparison and Benchmark Database (CCCBDB)
    for a given chemical formula and saves the retrieved data as a .csv file in a user-defined directory.
    """
    try:
        browser = mechanicalsoup.Browser()
        login_page = browser.get(url)
        login_html = login_page.soup

        form = login_html.select("form")[0]
        form.select("input")[0]["value"] = formula
        profiles_page = browser.submit(form, login_page.url)
        htmltable = profiles_page.soup.findAll('table')[1]
        list_table = table_data_text(htmltable)
        if list_table is not None:
            dftable = pd.DataFrame(list_table[1:], columns=list_table[0])
          #  dftable.to_csv(os.path.join(data_directory, f"{formula}.csv"), index=False)
            
            dftable.to_csv(formula+'.csv')
            
    except Exception as e:
        
        logging.error(f"Error in get_hform_data for {formula}: {e}")



def get_calculated_dipole_moment_data(formula, url="https://cccbdb.nist.gov/dipole1x.asp", data_directory='/data_directory/'):

    """
    This function retrieves calculated electric dipole moment data for a substance with a given chemical formula from 
    the Computational Chemistry Comparison and Benchmark Database (CCCBDB) database and saves the retrieved data in a .csv file
    """
    
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    
    browser = mechanicalsoup.Browser()
    login_page = browser.get(url)
    login_html = login_page.soup
    
    try:
        form = login_html.select("form")[0]
        form.select("input")[0]["value"] = formula
        profiles_page = browser.submit(form, login_page.url)
        htmltable = profiles_page.soup.find('table', attrs={'id': 'table2'})
        list_table = table_data_text(htmltable)
        dftable = pd.DataFrame(list_table[1:], columns=list_table[0])
        dftable.to_csv(data_directory + formula + '_dipole.csv', index=False)
     
    except Exception as e:
        error_message = f"Error processing {formula}: {e}"
        print(error_message)
        logging.error(error_message)
