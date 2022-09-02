import re
import os

class SearchKeywordPerformance:
    def __init__(self):
        pass

    def generate_search_keyword_performance(self, file_path):
        search_engine_ip_dict = {}
        search_engine_revenue = {}

        file = open(file_path,'r')
        header = file.readline()
        header_dict = {k.strip(): v for v, k in enumerate(header.split('\t'))}
        date = None

        line = file.readline()
        while(line is not None and line != ""):
            line_split = line.strip().split('\t')

            if(date is None):
                date = line_split[header_dict['date_time']].strip().split(' ')[0]

            ip = line_split[header_dict['ip']].strip()
            pagename = line_split[header_dict['pagename']].strip()
            page_url = line_split[header_dict['page_url']].strip()
            referrer = line_split[header_dict['referrer']].strip()
            products = line_split[header_dict['product_list']].strip()
            first_search = None

            #Ip coming for the first time.
            if(ip not in search_engine_ip_dict):
                # If referrer is an External page, store it for the future usage if a purchase happens.
                if('www.esshopzilla.com' not in referrer):
                    search_engine_ip_dict[ip] = [[page_url, referrer]]
                # If referrer is not an External page, no need to store anything.
                else:
                    pass
            else :
                # If referrer is an External page, store it for the future usage if a purchase happens.
                if('www.esshopzilla.com' not in referrer):
                    search_engine_ip_dict[ip].append([page_url, referrer])
                else:
                    page_info_list = search_engine_ip_dict[ip]
                    # Updating the map based on current referrer which is previous page_url.
                    for index in range(0, len(page_info_list)):
                        if(referrer == page_info_list[index][0]):
                            search_engine_ip_dict[ip][index] = [page_url, page_info_list[index][1]]
                            first_search = page_info_list[index][1]
                            break

            #Order is complete. Store revenue for the corresponding search.
            if(pagename == 'Order Complete' or page_url.lower() == 'https://www.esshopzilla.com/checkout/?a=complete'):
                product_list = products.split(',')
                revenue = sum([int(product.split(';')[3]) for product in product_list])

                if(first_search is not None):
                    search_content_result = re.search(r"\.(.+)\.com/.*(\?|&)(p|q)=([^&]+)", first_search)
                    search_domain = search_content_result.group(1).strip().lower()
                    search_keyword = search_content_result.group(4).strip().lower().replace("+"," ")

                    search_engine_revenue[search_domain + '\t' + search_keyword] = revenue + search_engine_revenue.get(search_domain + '\t' + search_keyword, 0)

            line = file.readline()

        with open(date+'_SearchKeywordPerformance.tab', 'w') as f:
            #Adding header to the output file
            f.write('Search Engine Domain\tSearch Keyword\tRevenue\n')
            for search in dict(sorted(search_engine_revenue.items(), key=lambda item: item[1], reverse = True)):
                f.write(search + '\t' + str(search_engine_revenue[search]) + '\n')
    print("Test-currentfile_path   " + os.getcwd())


SearchKeywordPerformance().generate_search_keyword_performance('data.tsv')
