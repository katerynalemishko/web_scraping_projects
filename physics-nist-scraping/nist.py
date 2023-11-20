import mechanicalsoup


def get_ionization_energy(atom,data_directory=data_directory):

  """
  This function fetches ionization energy data from NIST Atomic Spectra Database for a goven atomic species
  """

    url="https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html"

    browser = mechanicalsoup.Browser()
    login_page = browser.get(url)
    login_html = login_page.soup
    
    try:

        form = login_html.select("form")[0]
        form.select("input")[0]["value"] = atom
        profiles_page = browser.submit(form, login_page.url)
        
        htmltable=profiles_page.soup.findAll('table')[2]
 
        list_table = tableDataText(htmltable)
    
        dftable = pd.DataFrame(list_table[1:], columns=list_table[0])
        return dftable
     
    except Exception as e:
        
  
        print(f"Error processing {atom}: {e}")
