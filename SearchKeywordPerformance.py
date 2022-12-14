import re
import sys
import boto3
import os
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

class SearchKeywordPerformance:
    def __init__(self, file_path):
        self.file_path= file_path

    def generate_search_keyword_performance(self):
        search_engine_ip_dict = {}
        search_engine_revenue = {}
        try: 
            with open(self.file_path,'r') as file:
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

            optput_file_path_name = os.getcwd()+"/" + date+"_SearchKeywordPerformance.tab"
            object_name = date+"_SearchKeywordPerformance.tab"
        
            s3_client = boto3.client('s3')  
            response = s3_client.upload_file(optput_file_path_name, "keywork-performance-outputfile", object_name)
        
        except FileNotFoundError:
            msg = "Sorry, the file "+ self.file_path + "does not exist."
            print(msg)

        except(Exception) as ex:
            print("Exception occured")

# SearchKeywordPerformance('data.tsv').generate_search_keyword_performance()



if __name__ == "__main__":
    ## @params: [JOB_NAME]
    args = getResolvedOptions(sys.argv, ["VAL1","VAL2"])
    file_name=args['VAL1']
    bucket_name=args['VAL2']
    print("Bucket Name: " + bucket_name)
    print("File Name: " + file_name)
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, file_name, 'inpt_file1')
    file_path = os.getcwd()+"/inpt_file1"
     
    SearchKeywordPerformance(file_path).generate_search_keyword_performance()

