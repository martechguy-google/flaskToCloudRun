import scrapy
from ..Utils import *
from datetime import datetime
from gspread_dataframe import set_with_dataframe
import pandas as pd
import gspread
import json
import os


class DataSpider(scrapy.Spider):
    name = 'Data'

    # print("Enter Name for Output file:")
    # filenm = input()
    cmp = []
    count = 0
    def closed(self, reason):
        '''
        if not os.path.exists("Resources"):
            os.mkdir("Resources")'''
        gc = gspread.service_account(filename="creds/gcreds.json")
        #sheet = client.open_by_url(SAMPLE_SPREADSHEET_URL)
        sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1thQAn2EyGm52L10015IKC9fCHXxnFsMjslaKq1Jr_G0/edit#gid=0").worksheet("Data")
        df1 = pd.DataFrame(sh.get_all_records())
        df2 = pd.DataFrame(self.cmp)
        df = pd.concat([df2, df1])
        '''
        if os.path.exists("Resources/data.xlsx"):
            df1 = pd.read_excel("Resources/data.xlsx")
            df = pd.concat([df, df1])'''
        set_with_dataframe(sh, df)
        # df.to_excel("Resources/data.xlsx", index=False)
    
    def start_requests(self):
        df = pd.read_excel("Input/cities.xlsx")
        for _, item in df.iterrows():
            city = item["cities"]
            zip_code = item["zip code"]
            yield scrapy.Request(
                url=URL,
                method="POST",
                headers=headers,
                body=json.dumps(payload(str(zip_code))),
                meta={"city": city, "zip_code": zip_code},
                dont_filter=True,
                callback=self.parse
            )

    def parse(self, response):
        city = response.meta["city"]
        zip_code = response.meta["zip_code"]
        scrape_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        json_resp = json.loads(response.body)
        data = json_resp.get("data").get("pricingSet")
        check_dup = []
        storage_data = []
        for item in data.get("laborPricingGroupEntries"):
            storageTerm = item.get("storageTerm")
            name = storageTerm.get("name")
            rate_id = storageTerm.get("rateGroup").get("id")
            if name not in check_dup:
                check_dup.append(name)
                storage_data.append({
                    "name": name,
                    "rate_id": rate_id
                })
        orig_prices = {}
        for item in data.get("storagePricingGroupEntries"):
            pricing_data = item.get("pricing")
            plan_name = pricing_data.get("plan").get("name")
            amount = pricing_data.get("amount")
            plan_id = item.get("rateGroup").get("id")
            if plan_name == "Custom":
                continue
            p1 = plan_name.split("x")[0]
            p2 = plan_name.split("x")[-1]
            plan_name = f"{p1}' x {p2}'"
            for itm in storage_data:
                name = itm.get("name")
                rate_id = itm.get("rate_id")
                if plan_id == rate_id:
                    if name == "No commitment":
                        orig_prices[plan_name] = f'${round(amount)}'
        fnl = {}
        for item in data.get("storagePricingGroupEntries"):
            pricing_data = item.get("pricing")
            plan_name = pricing_data.get("plan").get("name")
            amount = pricing_data.get("amount")
            plan_id = item.get("rateGroup").get("id")
            if plan_name == "Custom":
                continue
            p1 = plan_name.split("x")[0]
            p2 = plan_name.split("x")[-1]
            plan_name = f"{p1}' x {p2}'"
            if plan_name not in list(fnl.keys()):
                fnl[plan_name] = []
            for itm in storage_data:
                name = itm.get("name")
                rate_id = itm.get("rate_id")
                if plan_id == rate_id:
                    if name == "No commitment":
                        fnl.get(plan_name).append({
                            "Scrape Date": scrape_date,
                            "Website": "Clutter",
                            "Store Name": "",
                            "Address": "",
                            "City": city,
                            "Zip Code": zip_code,
                            "Storage Size": plan_name,
                            "Term Length": storage_terms.get(name),
                            "Original Price": f'${round(amount)}',
                            "Discounted Price": ""
                        })
                    else:
                        fnl.get(plan_name).append({
                            "Scrape Date": scrape_date,
                            "Website": "Clutter",
                            "Store Name": "",
                            "Address": "",
                            "City": city,
                            "Zip Code": zip_code,
                            "Storage Size": plan_name,
                            "Term Length": storage_terms.get(name),
                            "Original Price": orig_prices.get(plan_name),
                            "Discounted Price": f'${round(amount)}'
                        })
        for _, item in fnl.items():
            item.reverse()
            for itm in item:
                self.cmp.append(itm)
        self.count += 1
        self.logger.info(f"Scraped ----------------> {self.count}")
