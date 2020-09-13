#!/bin/env python3
# Generates SQL statements for countries and municipalities
# Data for municipalities comes from the english wikipedia page: https://en.wikipedia.org/wiki/List_of_municipalities_of_Sweden
# Data for countries comes from the swedish wikipedia page: https://sv.wikipedia.org/wiki/Lista_över_självständiga_stater

def main():
    with open('app/database/sql/municipalities.txt', 'r') as wiki_file:
        line = wiki_file.readline()
        while line:
            start_of_name = line.find("[[") + 2
            end_of_name = line.find("Municipality") - 1
            name = line[start_of_name: end_of_name]

            if name == "":
                line = wiki_file.readline()
                continue

            print('INSERT INTO municipalities (id, name, created, "country", "area")')
            print("VALUES (uuid_generate_v4(), '{}', localtimestamp, '00000000-0000-0000-0000-000000000000', NULL);".format(name))
            print("")
            line = wiki_file.readline()

    with open('app/database/sql/countries.txt', 'r') as wiki_file:
        line = wiki_file.readline()
        while line:
            start_of_name = line.find("[[")

            if start_of_name is -1:
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

            print('INSERT INTO countries (id, name, created)')
            print("VALUES (uuid_generate_v4(), '{}', localtimestamp);".format(name))
            print("")
            line = wiki_file.readline()


if __name__ == "__main__":
    main()
