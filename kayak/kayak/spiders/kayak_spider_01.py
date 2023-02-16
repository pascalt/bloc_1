import scrapy
import re

cities = [
    "Mont Saint Michel",
    "St Malo",
    "Bayeux",
    "Le Havre",
    "Rouen",
    "Paris",
    "Amiens",
    "Lille",
    "Strasbourg",
    "Chateau du Haut Koenigsbourg",
    "Colmar",
    "Eguisheim",
    "Besancon",
    "Dijon",
    "Annecy",
    "Grenoble",
    "Lyon",
    "Gorges du Verdon",
    "Bormes les Mimosas",
    "Cassis",
    "Marseille",
    "Aix en Provence",
    "Avignon",
    "Uzes",
    "Nimes",
    "Aigues Mortes",
    "Saintes Maries de la mer",
    "Collioure",
    "Carcassonne",
    "Ariege",
    "Toulouse",
    "Montauban",
    "Biarritz",
    "Bayonne",
    "La Rochelle",
]

# giving id's to each city for the futur database storage
dict_cities = {cities[id]: id + 1 for id in range(len(cities))}


class KayakSpider01Spider(scrapy.Spider):
    name = "kayak_spider_01"
    allowed_domains = ["www.booking.com"]
    start_urls = ["http://www.booking.com/"]

    def parse(self, response):
        """Loop on each city and call the parse function for the hotels of the city"""

        # for each city parse
        for city_name, city_id in dict_cities.items():

            # constructing the url with the city name
            url_city = f"https://www.booking.com/searchresults.fr.html?ss={city_name}"

            # go to parse the hotels for the city
            yield response.follow(
                url=url_city,
                callback=self.parse_city,
                meta={"city_id": city_id, "city_name": city_name},
            )

    def parse_city(self, response):
        """Loop on each hotel to get name, booking link, score and call the parse function for the hotel page"""

        p = re.compile("https?:\/\/[a-z0-9\/:%_+.,#!@&=-]+\?")

        for hotel in response.xpath("//div[@data-testid='property-card']"):

            # retrieve the city id
            city_id = response.meta["city_id"]

            # retrieve the city name
            city_name = response.meta["city_name"]

            # get the hotel name
            name = hotel.xpath(".//div[@data-testid='title']//text()").get()

            # get the hotel link on booking
            booking_link = p.match(
                hotel.xpath(".//a[@data-testid='title-link']//@href").get()
            ).group()[:-1]

            # get the hotel score
            score = hotel.xpath(".//div[@class='b5cd09854e d10a6220b4']/text()").get()

            # change the "," into "." to the futur float
            if score is None:
                score = ""
            if "," in score:
                score = score.replace(",", ".")

            # go to parse the page of the hotel
            yield response.follow(
                url=booking_link,
                callback=self.parse_hotel,
                meta={
                    "city_id": city_id,
                    "city_name": city_name,
                    "name": name,
                    "booking_link": booking_link,
                    "score": score,
                },
            )

    def parse_hotel(self, response):

        """get the hotel latitude, longitude and description"""

        # retrieve the city id
        city_id = response.meta["city_id"]

        # retrieve the city name
        city_name = response.meta["city_name"]

        # retrieve the hotel name
        name = response.meta["name"]

        # retrieve the hotel link
        booking_link = response.meta["booking_link"]

        # retrieve the hotel score
        score = response.meta["score"]

        # get the hotel latitude and longitude
        lat_lon = response.xpath("//@data-atlas-latlng").get().split(",")

        # get the hotel description
        div_descr = response.xpath("//div[@id='property_description_content']")

        # put the hotel description from several trings into only one string
        descr = ""
        # for all the description paragraphs
        for p in div_descr.xpath(".//p/text()"):
            ch = p.get()
            # We don't need the redcution proposal on the description
            if not "réduction Genius" in ch and not "pour économiser." in ch:
                descr = descr + ch + "\n"

        # send all the hotel data scraped
        yield {
            "city_id": city_id,
            "city_name": city_name,
            "name": name,
            "booking_link": booking_link,
            "score": score,
            "lat": lat_lon[0],
            "lon": lat_lon[1],
            "descr": descr,
        }
