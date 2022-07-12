from bs4 import BeautifulSoup
import requests
import scrapper
import json

def getTotalNumberOfRecords():
    """
    This is the function retrieves the total number of pages .
    """
    try:
        html_text=requests.get('https://www.gov.uk/employment-tribunal-decisions?tribunal_decision_categories%5B%5D=age-discrimination&tribunal_decision_categories%5B%5D=disability-discrimination&tribunal_decision_categories%5B%5D=harassment&tribunal_decision_categories%5B%5D=parental-and-maternity-leave&tribunal_decision_categories%5B%5D=race-discrimination&tribunal_decision_categories%5B%5D=religion-or-belief-discrimination&tribunal_decision_categories%5B%5D=sex-discrimination&tribunal_decision_categories%5B%5D=sexual-orientation-discrimination-transexualism&tribunal_decision_categories%5B%5D=victimisation-discrimination').text
        soup =BeautifulSoup(html_text,'lxml')
        totalNoOfResult = int(soup.find('span',class_ = 'gem-c-pagination__link-label').text.split("of")[1])
        print(f"total number of results: {totalNoOfResult}")
        return totalNoOfResult
    except requests.exceptions.HTTPError as err:
        print ("Error",err)
    except requests.exceptions.Timeout:
        print ("Maybe set up for a retry, or continue in a retry loop")
    except requests.exceptions.TooManyRedirects:
        print("Tell the user their URL was bad and try a different one")
    except requests.exceptions.RequestException as e:
        print(f"catastrophic error. bail.{e}")
   

def getEmploymentTribunalDecision():
    """
    This  function retrieves  all records including the paginated results on the tribunal decision page .
    """
    try:
        for page in range(getTotalNumberOfRecords()):
            page_no=page + 1
            print(f"Retrieving page: {page_no}")
            html_text=requests.get('https://www.gov.uk/employment-tribunal-decisions?page='+str(page_no)+'&tribunal_decision_categories%5B%5D=age-discrimination&tribunal_decision_categories%5B%5D=disability-discrimination&tribunal_decision_categories%5B%5D=harassment&tribunal_decision_categories%5B%5D=parental-and-maternity-leave&tribunal_decision_categories%5B%5D=race-discrimination&tribunal_decision_categories%5B%5D=religion-or-belief-discrimination&tribunal_decision_categories%5B%5D=sex-discrimination&tribunal_decision_categories%5B%5D=sexual-orientation-discrimination-transexualism&tribunal_decision_categories%5B%5D=victimisation-discrimination').text
            soup =BeautifulSoup(html_text,'lxml')
            
            jobs = soup.find_all('li',class_= 'gem-c-document-list__item')
            for index,job in enumerate(jobs):
                link =job.find('a')['href']
                print(f"retrieving PDF on : {link}")
                getPDFpages('https://www.gov.uk'+link.strip())
    except requests.exceptions.HTTPError as err:
        print ("Error",err)
    except requests.exceptions.Timeout:
        print ("Maybe set up for a retry, or continue in a retry loop")
    except requests.exceptions.TooManyRedirects:
        print("Tell the user their URL was bad and try a different one")
    except requests.exceptions.RequestException as e:
        print(f"catastrophic error. bail {e}.")       


def getPDFpages(pdfUrlpage):
    """
    This  function retrieves  all the pdf links.
    """
    url =pdfUrlpage
    html_text=requests.get(url).text
    soup =BeautifulSoup(html_text,'lxml')
    #///////////////////////////////////
    #Judgement title 
    #///////////////////////////////////
    judgement_title = soup.find('h1',class_='gem-c-title__text govuk-heading-l').text.split(":",1)[0].strip()
    #///////////////////////////////////
    #Stagecoach manchester
    #///////////////////////////////////
    stagecoach_manchester =  soup.find('h1',class_='gem-c-title__text govuk-heading-l').text
    if stagecoach_manchester.find(":")!=-1:
        stagecoach_manchester= stagecoach_manchester.split(":",1)[1].strip()
    else:
        stagecoach_manchester= stagecoach_manchester
    print(f'stagecoach_manchester: {stagecoach_manchester}')

    #///////////////////////////////////
    # Judgement type
    #///////////////////////////////////
    judgement_type = soup.find('p',class_='gem-c-lead-paragraph').text

    #///////////////////////////////////
    #From
    #///////////////////////////////////
    from_loc_array = soup.find_all('dd',class_='gem-c-metadata__definition')[0].find_all('a')
    from_loc= ""
    for x in from_loc_array:
        from_loc =  from_loc + str(x.text) + " and " 
    print(from_loc)
    
    #///////////////////////////////////
    #Published Date
    #///////////////////////////////////
    published_date = soup.find_all('dd',class_='gem-c-metadata__definition')[1]
    for x in published_date:
        published_date = x.text.strip()
    
    #///////////////////////////////////
    #Country
    #///////////////////////////////////
    country = soup.find('dl',class_='app-c-important-metadata__list').find_all('dd',class_='app-c-important-metadata__definition')[0].find('a').text
    print(f'country: {country}')
    #///////////////////////////////////
    #jurisdiction_codes
    #///////////////////////////////////
    jurisdiction_codes = soup.find('dl',class_='app-c-important-metadata__list').find_all('dd',class_='app-c-important-metadata__definition')[1].find_all('a')
    all_jurisdiction_code =[]
    for index,job in enumerate(jurisdiction_codes):
        all_jurisdiction_code.append(job.text)
    
    print(all_jurisdiction_code)
    #///////////////////////////////////
    #Decision Date
    #///////////////////////////////////
    decision_date = soup.find('dl',class_='app-c-important-metadata__list').find_all('dd',class_='app-c-important-metadata__definition')[2].text
    print(f'decision_date: {decision_date}')
    
    #///////////////////////////////////
    #PDF Links and Names
    #///////////////////////////////////
    inp_str=soup.find('div',class_ = 'gem-c-govspeak govuk-govspeak').find_all('a')
    pdf_names =[]
    pdf_urls =[]
    for x in inp_str:
        print(f"Reading pdf on to be able to upload : {x['href']}")
        pdf_name=x.text.replace(" ", "").replace("/", "")
        scrapper.scrapper_main(pdf_name,x['href'])
        pdf_names.append(pdf_name)
        pdf_urls.append(x['href'])
    
    print(f'pdfs: {pdf_names}')  
    print(f'pdfs: {pdf_urls}')  
    #///////////////////////////////////
    #Save results into database table
    #///////////////////////////////////
    scrapper.update_db_result_after_scrapping(judgement_title,stagecoach_manchester,judgement_type,from_loc,published_date,country,json.dumps(all_jurisdiction_code),'',decision_date,json.dumps( pdf_urls ),json.dumps( pdf_names ))
     

if __name__ == '__main__':
    getEmploymentTribunalDecision()
    
  
                


    