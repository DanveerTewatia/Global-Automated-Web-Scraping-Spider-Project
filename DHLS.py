# -*- coding: utf-8 -*-
import scrapy
import pycountry
from locations.categories import Code
from locations.items import GeojsonPointItem

class DHLSpider(scrapy.Spider):
    name = "dhl_esp_dpa"
    brand_name = "DHL"
    spider_type = "chain"
    spider_chain_id = "6807"
    spider_categories = [
        Code.COURIERS.value
    ]
    spider_countries = [
        pycountry.countries.lookup("ESP").alpha_3
    ]

    def start_requests(self):
        yield scrapy.Request(
            url="https://wsbexpress.dhl.com/ServicePointLocator/restV3/servicepoints?servicePointResults=50&address=Q2FycmVyIGRlbCBNZXN0cmUgR296YWxibywgMTMsIEwnRWl4YW1wbGUsIDQ2MDA1IFZhbMOobmNpYSwgVmFsZW5jaWEsIFNwYWlu&countryCode=ES&capability=88,73,78,79&longitude=-0.3688546004638682&latitude=39.46520109326103&languageScriptCode=Latn&language=eng&languageCountryCode=GB&resultUom=mi&b64=true&key=963d867f-48b8-4f36-823d-88f311d9f6ef",
            method="GET",
            callback=self.parse,
        )

    def parse(self, response):
        data = response.json()
        list_of_places = data.get('servicePoints', [])
        
        for place in list_of_places:
            address = place.get('address', {})
            geo_location = place.get('geoLocation', {})
            contact_details = place.get('contactDetails', {})
            
            opening_hours = self.format_opening_hours(place.get('openingHours', {}))
            
            mappedAttributes = {
                'chain_name': self.brand_name,
                'chain_id': self.spider_chain_id,
                'ref': place.get('facilityId', ''),
                'name': place.get('servicePointNameFormatted', ''),
                'addr_full': f"{address.get('addressLine1', '')}, {address.get('city', '')}, {address.get('zipCode', '')}",
                'city': address.get('city', ''),
                'state': address.get('state', ''),
                'postcode': address.get('zipCode', ''),
                'country': address.get('country', ''),
                'phone': contact_details.get('phoneNumber', ''),
                'email': contact_details.get('email', ''),
                'website': contact_details.get('linkUri', ''),
                'lat': geo_location.get('latitude', ''),
                'lon': geo_location.get('longitude', ''),
                'opening_hours': opening_hours,
            }
            
            yield GeojsonPointItem(**mappedAttributes)

    def format_opening_hours(self, hours_data):
        formatted_hours = []
        for day in hours_data.get('openingHours', []):
            day_of_week = day['dayOfWeek'].capitalize()
            opening_time = day['openingTime']
            closing_time = day['closingTime']
            formatted_hours.append(f"{day_of_week}: {opening_time}-{closing_time}")
        return "; ".join(formatted_hours)