import os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def get_domain(s):
    # Strip scheme and optional "www." prefix to return the bare domain
    s = str(s).lower().split("/")[2]
    ss= s[4:] if s.startswith("www.") else s
    return ss


def extract_AI_overview(soup):
    """Extract AI Overview text, highlighted text, source links, and layout type from a SERP HTML snapshot."""
    ai_overview_text, AI_highlighted_text, overview_ai_link_list, link_domain_list, AIO_span_type = {'visible_text': None, 'hidden_text': None}, None, [], [], None

    # jsname="cUzNTd" marks the presence of an AI Overview block on the page
    if soup.find('div', jsname='cUzNTd'):
    
    
        # class "f5cPye" wraps all AI Overview content
        ai_overview_div = soup.find('div', class_='f5cPye')

        if ai_overview_div:
            # Detect a suppressed AIO: container exists but is styled as hidden with no "ZKfmAf" div
            element = soup.find('div', jsname='cUzNTd', class_='Fzsovc cwYVJe RJPOee')
            if element and element.get('style') != 'animation: auto ease 0s 1 normal none running none !important;' and not soup.find('div', class_='ZKfmAf'):
                AIO_span_type ="surpressed_AIO"
      
            
    
            # Collect AIO body spans, skipping those inside citation list items (class "LLtSOc")
            span_elements = [span for span in ai_overview_div.find_all('span')
                if not span.find_parent('li', class_='LLtSOc')]

            visible_text = []
            hidden_text = []
            
            processed_parents = set()

            
            for span in span_elements:
                nested_span = span.find('span')
                if nested_span:
                    links = nested_span.find_all('a', class_='DTlJ6d')
                    # Two or more citation links signals the standard (non-suppressed) AIO layout
                    if len(links) >= 2 and nested_span.get('aria-hidden') != 'true' and AIO_span_type !="surpressed_AIO":
                        AIO_span_type ="nested_span_2_links"

                # Leaf span with no children — extract text directly
                if not span.find('span') and not (span.get('class') == ['M5tQyf'] and span.find('a', jsname='TGaAqd')):
                    text = span.get_text(" ", strip=True)

                    if text:  # Only process non-empty spans
                        if span.get('aria-hidden') == 'true' or span.find_parent('div', class_='bsmXxe'):
                            hidden_text.append(text)
                        else:
                            visible_text.append(text)
                # Handle AIO text embedded with an inline <a> link (class "M5tQyf")
                elif not span.find('span') and (span.get('class') == ['M5tQyf'] and span.find('a', jsname='TGaAqd')):
                    parent_span = span.find_parent('span')
                    parent_id = str(parent_span)  # track processed parents to avoid duplicate text
                    if parent_id not in processed_parents:
                        text = parent_span.get_text(" ", strip=True)
                        if text:
                            if span.get('aria-hidden') == 'true' or span.find_parent('div', class_='bsmXxe'):
                                hidden_text.append(text)
                            else:
                                visible_text.append(text)
                        processed_parents.add(parent_id)
       


            ai_overview_text = {
                'visible_text': ' '.join(visible_text) if visible_text else None,
                'hidden_text': ' '.join(hidden_text) if hidden_text else None
            }
        else:
            ai_overview_text = {'visible_text': None, 'hidden_text': None}

        if ai_overview_div:
            # Extract highlighted (bolded) text; skip aria-hidden duplicates
            highlighted_texts = ai_overview_div.find_all('mark', class_='QVRyCf', attrs={'aria-hidden': None})
            AI_highlighted_text = " ".join(text.get_text(strip=True) for text in highlighted_texts) if highlighted_texts else None

        # Source links are listed in the citation strip (class "TRXNOc")
        ai_overview_link_part = soup.find('div', class_='TRXNOc')
        if ai_overview_link_part:
            AI_link_tag = ai_overview_link_part.find_all('a', href=True)

            for each_link in AI_link_tag:
                each_url = each_link['href']
                if each_url:
                    overview_ai_link_list.append(each_url)

            overview_ai_link_list = list(set(overview_ai_link_list))
    if len(overview_ai_link_list)>0:
        link_domain_list = list(set([get_domain(each_url) for each_url in overview_ai_link_list]))
        
    return ai_overview_text, AI_highlighted_text, overview_ai_link_list, link_domain_list, AIO_span_type




def extract_featured_snippet(soup, filename):
    """Extract featured snippet text, highlighted text, source links, and layout type from a SERP HTML snapshot."""
    snippet_type, featured_snippet_list, featured_snippet_link_list, highlighted_snippet_list, featured_snippet_domain_list, span_type = None,[],[], [], [], None

    # class "hELpae" is only present when a featured snippet exists on the page
    if soup.find("span", class_="hELpae"):

        # Snippet-related content lives inside class "MjjYud" or "ifM9O"
        for mjjyud_div in soup.find_all('div', class_=['MjjYud', "ifM9O"]):
            
            v3f_div = mjjyud_div.find('div', class_='V3FYCf')
            if v3f_div:

                # hgKElc / di3YZe hold the snippet body; their presence distinguishes layout variants
                hgkelc = v3f_div.find(["div",'span'], class_=['hgKElc', "di3YZe"])
                di3YZe = v3f_div.find("div", class_= "di3YZe")
                

                if not hgkelc:
                    snippet_type ="single"
                    span_type = "no_span"
                    
                    
                if hgkelc and snippet_type!="multiple":
         
                    snippet_type ="single"
                    nested_spans = hgkelc.find_all('span', recursive=True)
                    if len(nested_spans) == 0:
                        span_type = "single_span"
                        
                        if not di3YZe:
                            featured_snippet_text = hgkelc.get_text(strip=False)
                        else:
                            heading = soup.find(class_="co8aDb")
                            if heading:
                                heading_text = heading.get_text(strip=True)
                                first_ol = soup.select_one('ol.X5LH0c')
                                list_items = first_ol.find_all("li", class_="TrT0Xe") if first_ol else []
                                numbered_list = [f"{i+1}. {item.text}" for i, item in enumerate(list_items)]
                                featured_snippet_text = heading_text + "  " + "  ".join(numbered_list)
                                span_type = "listed_FS"
                            else:
                                # Fallback for di3YZe layout without a heading element
                                featured_snippet_text = hgkelc.get_text(separator='. ', strip=False)

                        featured_snippet_list.append(featured_snippet_text)


                        b_tags = hgkelc.find('b')
                        if b_tags and not di3YZe:
                            highlighted_snippet = b_tags.get_text(strip=True)
                            highlighted_snippet_list.append(highlighted_snippet)
                        else:
                            highlighted_snippet_list=[]
                            
                    else:
                        span_type = "nested_span"
                        outer_span = hgkelc.find('span')
                        if outer_span:
                            # Remove layout-only divs to avoid noise in the extracted text
                            excluded_divs = outer_span.find_all('div', class_=['LXUB1d wHYlTd', 'q3y9Kc Pqkn2e', 'Fy3QE' ])
                            for div in excluded_divs:
                                div.extract()

                            # Decompose tooltip divs that would add duplicate text
                            for tooltip in outer_span.find_all('div', class_='nnFGuf'):
                                tooltip.decompose()
                            featured_snippet_text = outer_span.get_text(strip=False)

                            if featured_snippet_text:
                                featured_snippet_list.append(featured_snippet_text)

                            b_tags = hgkelc.find('b')
                            if b_tags:
                                highlighted_snippet = ' '.join(b_tags.stripped_strings)
                                highlighted_snippet_list.append(highlighted_snippet)
                    
                    

                    # Source link for a single snippet uses jsname="UWckNb"
                    link_tag = soup.find('a', jsname='UWckNb')


                    if link_tag:
                        featured_snippet_link = link_tag['href']
                        featured_snippet_link_list.append(featured_snippet_link)

                    break
            # Multiple featured snippets are each wrapped in class "Boshpf"
            boshpf_spans = mjjyud_div.find_all('span', class_='Boshpf')
            if boshpf_spans:
                snippet_type ="multiple"

                for boshpf_each in boshpf_spans:
                    featured_snippet_text = boshpf_each.get_text(strip=False)
                    featured_snippet_list.append(featured_snippet_text)
                    b_tags_boshpf_each = boshpf_each.find('b')
                    if b_tags_boshpf_each:
                        highlighted_snippet_each = b_tags_boshpf_each.get_text(strip=False)
                        highlighted_snippet_list.append(highlighted_snippet_each)


                # Each result card (class "wep10b") may have its own source link
                wep10b_div = mjjyud_div.find_all('div', class_='wep10b')
                for each_wep10b in wep10b_div:
                    link_tag = each_wep10b.find('a', href=True)
                    if link_tag:

                        featured_snippet_link = link_tag['href']

                        featured_snippet_link_list.append(featured_snippet_link)
                break 
    if len(featured_snippet_link_list)>0:
        try:
            featured_snippet_domain_list = list(set([get_domain(each_url) for each_url in featured_snippet_link_list]))
        except:
            featured_snippet_domain_list = []

    return snippet_type, featured_snippet_list, highlighted_snippet_list, featured_snippet_link_list, featured_snippet_domain_list, span_type


# Set up headless Chrome browser (needed to render dynamic JS in saved HTML files)
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

def convert_timestamp(timestamp):
    timestamp = str(timestamp)
    return timestamp

# Path to the folder containing HTML files
folder_path = "/xxx/"
data = []
b1 = time.time()
indx_count = 0

for filename in os.listdir(folder_path):
    if filename.endswith('.html') and not filename.startswith('test'):
        indx_count +=1
        if indx_count%100==0:
            print("\n processing index :", indx_count)
            print("\n processing this file:", filename)

        # Filename format: <index>_<timestamp>.html
        based_filename = filename[:-5]  # Remove '.html'
        index, timestamp = based_filename.split('_', 1)
        timestamp = convert_timestamp(timestamp)
        full_path = os.path.join(folder_path, filename)
        file_uri = 'file://' + os.path.abspath(full_path)
        time.sleep(1)
        driver.get(file_uri)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        ai_overview_text, AI_highlighted_text, overview_ai_link_list, link_domain_list, AIO_span_type = extract_AI_overview(soup)
        snippet_type, featured_snippet_list, highlighted_snippet_list, featured_snippet_link_list, featured_snippet_domain_list, span_type = extract_featured_snippet(soup, filename)
        data.append({'new_index': index, 'Timestamp': timestamp, 'AI_overview_answer_visible': ai_overview_text["visible_text"],'AI_overview_answer_hidden': ai_overview_text["hidden_text"], "AI_highlighted_text":AI_highlighted_text, \
               "links_of_AI_overview":overview_ai_link_list, "domains_of_AI_overview":link_domain_list,"AIO_span_type":AIO_span_type, "featured_snippet_type":snippet_type, \
               "featured_snipet_texts":featured_snippet_list, "highlighted_snippet_texts":highlighted_snippet_list,"featured_snippet_links":featured_snippet_link_list, "featured_snippet_domains":featured_snippet_domain_list,"snippet_span_type":span_type })

driver.quit()

# Create a DataFrame and save results to CSV
df = pd.DataFrame(data)
location_str ="NYC"
df.to_csv(location_str+"_snippet_and_AI_overview.csv", index=False)
print("\n\n nested span distribution:", df["snippet_span_type"].value_counts())
print("\n\n AIO_span_type  distribution:", df["AIO_span_type"].value_counts())
e1 = time.time()
print("time used:", e1-b1)
