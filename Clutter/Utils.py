URL = "https://www-api.clutter.com/graphql"


headers = {
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

def payload(zip_code):
    return {"operationName":"PricingSet","variables":{"zip":zip_code,"visitorToken":"43305b87-8138-49e1-a2ff-80d5bffeb705"},"query":"query PricingSet($zip: String!, $visitorToken: String!) {\n  pricingSet(zip: $zip, visitorToken: $visitorToken) {\n    ...pricingSet\n    __typename\n  }\n}\n\nfragment pricingSet on PricingSet {\n  id\n  quoteId\n  marketPricingVariantLabel\n  storagePricingGroupEntries {\n    ...pricingGroupPricingEntry\n    __typename\n  }\n  laborPricingGroupEntries {\n    ...pricingGroupLaborEntry\n    __typename\n  }\n  __typename\n}\n\nfragment pricingGroupPricingEntry on PricingGroupPricingEntry {\n  id\n  rateGroup {\n    ...rateGroup\n    __typename\n  }\n  pricing {\n    ...pricing\n    __typename\n  }\n  __typename\n}\n\nfragment rateGroup on RateGroup {\n  id\n  name\n  __typename\n}\n\nfragment pricing on Pricing {\n  id\n  amount\n  plan {\n    ...plan\n    __typename\n  }\n  __typename\n}\n\nfragment plan on Plan {\n  id\n  name\n  kind\n  cuft\n  __typename\n}\n\nfragment pricingGroupLaborEntry on PricingGroupLaborEntry {\n  id\n  rateGroup {\n    ...rateGroup\n    __typename\n  }\n  laborPolicy {\n    ...laborPolicy\n    __typename\n  }\n  storageTerm {\n    ...storageTerm\n    __typename\n  }\n  __typename\n}\n\nfragment laborPolicy on LaborPolicy {\n  id\n  laborBillingFormat\n  perItemPricing\n  __typename\n}\n\nfragment storageTerm on StorageTerm {\n  id\n  name\n  rateGroup {\n    ...rateGroup\n    __typename\n  }\n  __typename\n}\n"}

storage_terms = {
    "8 months commitment": "8 months +",
    "4 months commitment": "4 months +",
    "No commitment": "Month to month"
}
