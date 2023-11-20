import mechanicalsoup
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re


def scrape_chemspider(formula):

  """
  This function returns some useful information (like substance name, substance molecular mass, 
  subrastance url on ChemSpider etc.) for all isomers having a given chemical formula
  """
    
    my_url="http://www.chemspider.com/Search.aspx?q="+str(formula)
    
    uClient=urlopen(my_url)
    page_html=uClient.read()
    uClient.close()
    
    page_soup=BeautifulSoup(page_html,"html.parser")
    target=page_soup.findAll("div",{"class":"results-wrapper table"})
    target=target[0]
    
    base_url="http://www.chemspider.com/Chemical-Structure."
    results=target.div.table.tbody.findAll("tr")
    scraped_data=[{"ID":None,"URL":None,"img_url":None,"Molecular Formula":None,"Molecular Weight":None,"Name":None} for i in range(0,len(results))]
    
    for i in range(0,len(results)):
        result=results[i].findAll("td")
        scraped_data[i]["ID"]=result[0].a.text.strip()
        scraped_data[i]["URL"]=base_url+str(scraped_data[i]["ID"])+".html"
        scraped_data[i]["img_url"]="http://www.chemspider.com/ImagesHandler.ashx?id="+str(scraped_data[i]["ID"])+"&w=250&h=250"
        scraped_data[i]["Molecular Formula"]=result[2].text.strip()
        names=result[2].findAll("<sub>")
        
        for name in names:
            scraped_data[i]["Molecular Formula"]+=str(name.sub).strip()
        scraped_data[i]["Molecular Weight"]=result[3].text.strip()
        scraped_data[i]["Name"]=scrape_id_page(base_url+str(scraped_data[i]["ID"])+".html")
    return scraped_data


def scrape_id_page(url):

  """
  this function fetches a web page from the given URL, parses its HTML content, finds a specific <span> element
  with a particular ID, and returns the text content of that element.
  """
    
    uClient=urlopen(url)
    page_html=uClient.read()
    uClient.close()
    page_soup=soup(page_html,"html.parser")
    target=page_soup.findAll("span",{"id":"ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewDetails_rptDetailsView_ctl00_WrapTitle"})
    
    return target[0].text.strip()


def get_smiles_from_chemspider(url):

  
"""
This function fetches a SMILES structure data for a given substance using its URL on ChemSpider
"""

  
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        download_button = soup.find('button', {'title': 'Save'})

        if download_button:
            onclick_value = download_button.get('onclick')
            download_link = re.search(r"'(.*?)'", onclick_value).group(1)
            download_link = 'http://www.chemspider.com' + download_link
            download_response = requests.get(download_link)

            data = download_response.content.decode('utf-8') 

            start_index = data.find('> <SMILES>')
            if start_index != -1:
                end_index = data.find('\r\n\r\n', start_index + len('> <SMILES>'))
                smiles_data = data[start_index + len('> <SMILES>') : end_index].strip()

        return smiles_data
    else:
        print('Failed to fetch the webpage.')



def get_all_smiles_from_formula(formula):

"""
This function fetches form ChemSpider all isomer names and their correponding SMILES structures for a given chemical formula
"""
  
    info_dict = scrape_chemspider(formula)
    all_smiles = []

    for info in info_dict:
        url = info['URL']
        name = info['Name']

        try:
            smiles = get_smiles_from_chemspider(url)
            all_smiles.append({'Name': name, 'SMILES': smiles})
        except Exception as e:
            all_smiles.append({'Name': name, 'SMILES': 'Error: ' + str(e)})

    return all_smiles
