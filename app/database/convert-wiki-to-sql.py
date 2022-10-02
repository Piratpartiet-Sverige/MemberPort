#!/bin/env python3
# Generates SQL statements for countries and municipalities
# Data for countries comes from the swedish wikipedia page: https://sv.wikipedia.org/wiki/Lista_över_självständiga_stater
import locale

norrbotten = ["Arjeplog", "Arvidsjaur", "Boden", "Gällivare", "Haparanda", "Jokkmokk", "Kalix", "Kiruna", "Luleå", "Pajala", "Piteå",
              "Älvsbyn", "Överkalix", "Övertorneå"]

vasterbotten = ["Bjurholm", "Dorotea", "Lycksele", "Malå", "Nordmaling", "Norsjö", "Robertsfors", "Skellefteå", "Sorsele", "Storuman",
                "Umeå", "Vilhelmina", "Vindeln", "Vännäs", "Åsele"]

jamtland_harjedalen = ["Berg", "Bräcke", "Härjedalen", "Krokom", "Ragunda", "Strömsund", "Åre", "Östersund"]

vasternorrland = ["Härnösand", "Kramfors", "Sollefteå", "Sundsvall", "Timrå", "Ånge", "Örnsköldsvik"]

gavleborg = ["Bollnäs", "Gävle", "Hofors", "Hudiksvall", "Ljusdal", "Nordanstig", "Ockelbo", "Ovanåker", "Sandviken", "Söderhamn"]

dalarna = ["Avesta", "Borlänge", "Falun", "Gagnef", "Hedemora", "Leksand", "Ludvika", "Malung-Sälen", "Mora", "Orsa", "Rättvik",
           "Smedjebacken", "Säter", "Vansbro", "Älvdalen"]

uppsala = ["Enköping", "Heby", "Håbo", "Knivsta", "Tierp", "Uppsala", "Älvkarleby", "Östhammar"]

vastmanland = ["Arboga", "Fagersta", "Hallstahammar", "Kungsör", "Köping", "Norberg", "Sala", "Skinnskatteberg", "Surahammar", "Västerås"]

orebro = ["Askersund", "Degerfors", "Hallsberg", "Hällefors", "Karlskoga", "Kumla", "Laxå", "Lekeberg", "Lindesberg", "Ljusnarsberg",
          "Nora", "Örebro"]

sormland = ["Eskilstuna", "Flen", "Gnesta", "Katrineholm", "Nyköping", "Oxelösund", "Strängnäs", "Trosa", "Vingåker"]

ostergotland = ["Boxholm", "Finspång", "Kinda", "Linköping", "Mjölby", "Motala", "Norrköping", "Söderköping", "Vadstena", "Valdemarsvik",
                "Ydre", "Åtvidaberg", "Ödeshög"]

blekinge = ["Karlshamn", "Karlskrona", "Olofström", "Ronneby", "Sölvesborg"]

stockholm = ["Botkyrka", "Danderyd", "Ekerö", "Haninge", "Huddinge", "Järfälla", "Lidingö", "Nacka", "Norrtälje", "Nykvarn", "Nynäshamn",
             "Salem", "Sigtuna", "Sollentuna", "Solna", "Stockholm", "Sundbyberg", "Södertälje", "Tyresö", "Täby", "Upplands-Bro",
             "Upplands Väsby", "Vallentuna", "Vaxholm", "Värmdö", "Österåker"]

varmland = ["Arvika", "Eda", "Filipstad", "Forshaga", "Grums", "Hagfors", "Hammarö", "Karlstad", "Kil", "Kristinehamn", "Munkfors",
            "Storfors", "Sunne", "Säffle", "Torsby", "Årjäng"]

vastra_gotaland = ["Ale", "Alingsås", "Bengtsfors", "Bollebygd", "Borås", "Dals-Ed", "Essunga", "Falköping", "Färgelanda", "Grästorp",
                   "Gullspång", "Göteborg", "Götene", "Herrljunga", "Hjo", "Härryda", "Karlsborg", "Kungälv", "Lerum", "Lidköping",
                   "Lilla Edet", "Lysekil", "Mariestad", "Mark", "Mellerud", "Munkedal", "Mölndal", "Orust", "Partille", "Skara", "Skövde",
                   "Sotenäs", "Stenungsund", "Strömstad", "Svenljunga", "Tanum", "Tibro", "Tidaholm", "Tjörn", "Tranemo", "Trollhättan",
                   "Töreboda", "Uddevalla", "Ulricehamn", "Vara", "Vårgårda", "Vänersborg", "Åmål", "Öckerö"]

halland = ["Falkenberg", "Halmstad", "Hylte", "Kungsbacka", "Laholm", "Varberg"]

skane = ["Bjuv", "Bromölla", "Burlöv", "Båstad", "Eslöv", "Helsingborg", "Hässleholm", "Höganäs", "Hörby", "Höör", "Klippan",
         "Kristianstad", "Kävlinge", "Landskrona", "Lomma", "Lund", "Malmö", "Osby", "Perstorp", "Simrishamn", "Sjöbo", "Skurup",
         "Staffanstorp", "Svalöv", "Svedala", "Tomelilla", "Trelleborg", "Vellinge", "Ystad", "Åstorp", "Ängelholm", "Örkelljunga",
         "Östra Göinge"]

jonkoping = ["Aneby", "Eksjö", "Gislaved", "Gnosjö", "Habo", "Jönköping", "Mullsjö", "Nässjö", "Sävsjö", "Tranås", "Vaggeryd", "Vetlanda",
             "Värnamo"]

kronoberg = ["Alvesta", "Lessebo", "Ljungby", "Markaryd", "Tingsryd", "Uppvidinge", "Växjö", "Älmhult"]

kalmar = ["Borgholm", "Emmaboda", "Hultsfred", "Högsby", "Kalmar", "Mönsterås", "Mörbylånga", "Nybro", "Oskarshamn", "Torsås", "Vimmerby",
          "Västervik"]

gotland = ["Gotland"]


def main():
    name = ""
    area = "NULL"
    municipalities = (norrbotten + vasterbotten + jamtland_harjedalen + vasternorrland + gavleborg + dalarna + uppsala + vastmanland +
                      orebro + sormland + ostergotland + blekinge + stockholm + varmland + vastra_gotaland + halland + skane + jonkoping +
                      kronoberg + kalmar + gotland)
    municipalities = sorted(municipalities, key=locale.strcoll)

    for municipality in municipalities:
        if municipality in norrbotten:
            area = "6"
        elif municipality in vasterbotten:
            area = "7"
        elif municipality in jamtland_harjedalen:
            area = "8"
        elif municipality in vasternorrland:
            area = "9"
        elif municipality in gavleborg:
            area = "10"
        elif municipality in dalarna:
            area = "11"
        elif municipality in uppsala:
            area = "12"
        elif municipality in vastmanland:
            area = "13"
        elif municipality in orebro:
            area = "14"
        elif municipality in sormland:
            area = "15"
        elif municipality in ostergotland:
            area = "16"
        elif municipality in blekinge:
            area = "17"
        elif municipality in stockholm:
            area = "18"
        elif municipality in varmland:
            area = "19"
        elif municipality in vastra_gotaland:
            area = "20"
        elif municipality in halland:
            area = "21"
        elif municipality in skane:
            area = "22"
        elif municipality in jonkoping:
            area = "23"
        elif municipality in kronoberg:
            area = "24"
        elif municipality in kalmar:
            area = "25"
        elif municipality in gotland:
            area = "26"

        print('INSERT INTO mp_municipalities (id, name, created, "country", "area")')
        print("VALUES (uuid_generate_v4(), '{}', localtimestamp, '00000000-0000-0000-0000-000000000000', {});".format(municipality, area))
        print("")

    with open('app/database/sql/countries.txt', 'r') as wiki_file:
        line = wiki_file.readline()
        while line:
            start_of_name = line.find("[[")

            if start_of_name == -1:
                line = wiki_file.readline()
                continue
            else:
                start_of_name += 2

            end_of_name = line.find("]]")
            name = line[start_of_name: end_of_name]

            if name == "" or name == "-" or name == " " or name == "}":
                line = wiki_file.readline()  # Skip year line
                line = wiki_file.readline()
                continue
            else:
                wiki_file.readline()  # Skip year line

            print('INSERT INTO mp_countries (id, name, created)')
            print("VALUES (uuid_generate_v4(), '{}', localtimestamp);".format(name))
            print("")
            line = wiki_file.readline()


if __name__ == "__main__":
    main()
