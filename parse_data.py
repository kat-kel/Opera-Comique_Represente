import csv
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Float
ENCODING = 'utf-8'


def main():
    place_data = create_data_place()
    opera_data = create_data_opera()
    performance_data = create_data_performance(opera_data)
    person_data = create_data_person()
    responsibility_data = create_data_responsibility(performance_data, person_data)

    engine = create_engine('sqlite:///bd.db')

    insert_data_commune(place_data, engine)
    insert_data_paris(performance_data, engine)
    insert_data_opera(opera_data, engine)
    insert_data_person(person_data, engine)
    insert_data_responsibility(responsibility_data, engine)


def create_data_place():
    """
    Parses a local csv file and returns a list of commune data. The keys represent the commune's unique primary key,
    commune's name, and commune's department number.
    Relevant headers in the csv file are: 'Nom de l'unité d'analyse', 'Code du département'
    :return: list of dictionaries with keys:
                                            id_commune (unique primary key, int)
                                            commune (name of commune, string)
                                            dep (department code, int)
    """
    with open("data/communesINSEE.csv", "r", encoding=ENCODING) as f:
        # csv exported from Excel file at https://www.insee.fr/fr/statistiques/fichier/2653233/REC_T12.xls
        reader = csv.DictReader(f)  # process the lists as a csv file with first line as keys
        output = []
        count = 0
        for row in reader:
            if row["Code du département"] != "0":  # only treat data from a department
                count += 1  # update primary key
                output.append({"id_commune": int(count),
                               "commune": str(row["Nom de l'unité d'analyse"]),
                               "dep": int(row["Code du département"])
                               })
            else:  # ignore country-level data, i.e. France with department number 0
                pass
        return output


def insert_data_commune(data, engine):
    table_name = 'communes'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                  Column('id_commune', Integer, primary_key=True),
                  Column('commune', String),
                  Column('dep', Integer),
                  )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(),data)


def create_data_opera():
    """
    Parses local csv file and returns dataset of unique works, each with a unique id.
    :return: list of dictionaries with keys:
                                            id_work (unique primary key, int)
                                            id_charlton (numeric code given in Wild/Charlton 2005, int)
                                            title (name of the work, string)
                                            date_creation (date of the work's world premiere, datetime)
                                            acts (quantity of acts, int)
    """
    with open("data/database_raw.csv", "r", encoding=ENCODING) as f:
        reader = csv.DictReader(f)
        data = []
        count = 0
        for row in reader:
            data.append([
                int(row["id_charlton"]),
                str(row["title"]),
                datetime.strptime(row["date_creation"][0:10], '%Y-%m-%d'),
                int(row["acts"])
            ])
        for i, e in enumerate(data):
            data[i] = tuple(e)
        unique_data = list(set(data))
        output = []
        count = 0
        for i in sorted(unique_data):
            count += 1
            output.append({
                "id_opera":int(count),
                "id_charlton":i[0],
                "title":i[1],
                "date_creation":i[2],
                "acts":i[3]
            })
    return output


def insert_data_opera(data, engine):
    table_name = 'opera'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                  Column('id_opera', Integer, primary_key=True),
                  Column('id_charlton', Integer),
                  Column('title', String),
                  Column('acts', Integer),
                  Column('date_creation', DateTime)
                  )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(),data)


def create_data_performance(work_data):
    """
    Parses local csv file and returns dataset of performances. Data represent the performance's unique primary key,
    work's title, work's id in Wild/Charlton 'Théâtre de l'Opéra-Comique Paris' (2005), and the performance's datetime
    Relevant headers in the csv file are: 'title', 'id_charlton', 'date_performance'
    :return: list of dictionaries with keys:
                                            id_performance (unique primary key, int)
                                            title (name of work, string)
                                            charlton_id (numeric code given in Wild/Charlton 2005, int)
                                            date_performance (date of performance, datetime)
                                            source (code for what primary source supports this datum, string)
                                            age (difference between premiere and performance, float)
                                            authors (list of 9 names/values & position says what the role is, list)
    """
    with open("data/database_raw.csv", "r", encoding=ENCODING) as f:
        reader = csv.DictReader(f)
        output = []
        count = 0
        for row in reader:
            for d in work_data:
                if row["title"] == d["title"]:
                    delta = datetime.strptime(row["date_performance"][0:10], '%Y-%m-%d') \
                            - datetime.strptime(row["date_creation"][0:10], '%Y-%m-%d')
                    count += 1
                    opera_id = d["id_opera"]
                    output.append({
                        "id_performance": int(count),
                        "title": str(row["title"]),
                        "opera_id":opera_id,
                        "charlton_id": int(row["id_charlton"]),
                        "date_performance": datetime.strptime(row["date_performance"][0:10], '%Y-%m-%d'),
                        "source":row["source"],
                        "age": delta.days / 365,
                        "authors":[row["Compositeur (1)"], row["Compositeur (2)"], row["Compositeur (3)"],
                                   row["Librettiste (1)"], row["Librettiste (2)"], row["Librettiste (3)"],
                                   row["Librettiste (arr.) 1"], row["Librettiste (arr.) 2"], row["Librettiste (arr.) 3"]]
                })
    return output


def insert_data_paris(data, engine):
    table_name = 'paris'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                  Column('id_performance', Integer, primary_key=True),
                  Column('title', String),
                  Column('opera_id', Integer),  # foreign key
                  Column('date_performance', DateTime),
                  Column('source', String),
                  Column('age', Float)
                  )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(),data)


def create_data_person():
    """
    Parses local csv file and returns dataset of unique people, each with a unique id.
    :return: list of dictionaries with keys:
                                            id_person (unique primary key, int)
                                            name (name of the librettist/composer/translator, string)
    """
    with open("data/database_raw.csv", "r", encoding=ENCODING) as f:
        reader = csv.DictReader(f)
        data = set()
        for row in reader:
            if row["Compositeur (1)"] != '' and row["Compositeur (1)"] != '0':
                data.add(str(row["Compositeur (1)"]))
            if row["Compositeur (2)"] != '' and row["Compositeur (2)"] != '0':
                data.add(str(row["Compositeur (2)"]))
            if row["Compositeur (3)"] != '' and row["Compositeur (3)"] != '0':
                data.add(str(row["Compositeur (3)"]))
            if row["Librettiste (1)"] != '' and row["Librettiste (1)"] != '0':
                data.add(str(row["Librettiste (1)"]))
            if row["Librettiste (2)"] != '' and row["Librettiste (2)"] != '0':
                data.add(str(row["Librettiste (2)"]))
            if row["Librettiste (3)"] != '' and row["Librettiste (3)"] != '0':
                data.add(str(row["Librettiste (3)"]))
            if row["Librettiste (arr.) 1"] != '' and row["Librettiste (arr.) 1"] != '0':
                data.add(str(row["Librettiste (arr.) 1"]))
            if row["Librettiste (arr.) 2"] != '' and row["Librettiste (arr.) 2"] != '0':
                data.add(str(row["Librettiste (arr.) 2"]))
            if row["Librettiste (arr.) 3"] != '' and row["Librettiste (arr.) 3"] != '0':
                data.add(str(row["Librettiste (arr.) 3"]))
        output = []
        count = 0
        for i in sorted(data):
            count += 1
            output.append({
                "id_person":int(count),
                "name":i
            })
    return output


def insert_data_person(data, engine):
    table_name = 'person'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                    Column('id_person', Integer, primary_key=True),
                    Column('name', String),
                    )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(), data)


def create_data_responsibility(performance_data, person_data):
    """
    Parses lists of dictionaries generated in previously called functions and synthesizes relevant data for table of
    association between performances and authors.
    :param performance_data: list of dictionaries; relevant keys are: title, id_charlton, date_performance, authors
    :param person_data: list of dictionaries; relevant keys are: name, id_person
    :return: list of dictionaries with keys:
                                            id_responsibility (unique primary key, int)
                                            title (name of the work, string)
                                            opera_id (foreign key, int)
                                            performance_date (date of performance, datetime)
                                            performance_id (foreign key, int)
                                            person (name of composer/librettist/translator, string)
                                            person_id (foreign key, int)
                                            role (the nature of the person's contribution to the work, string)

    """
    output = []
    count = 0
    for row in performance_data:
        for i in range(6):
            if row["authors"][i] != '0' and row["authors"][i] != '':
                count += 1
                if i < 3:
                    role = "composer"
                elif i > 5:
                    role = "translator"
                else:
                    role = "librettist"
                for p in person_data:
                    if row["authors"][i] == p["name"]:
                        person_id = p["id_person"]
                output.append({
                    "id_responsibility":int(count),
                    "title":row["title"],
                    "opera_id": row["opera_id"],
                    "performance_date":row["date_performance"],
                    "performance_id":row["id_performance"],
                    "name": row["authors"][i],
                    "person_id":person_id,
                    "role":role
                })
    return output


def insert_data_responsibility(data, engine):
    table_name = 'responsibility'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                    Column('id_responsibility', Integer, primary_key=True),
                    Column('title', String),
                    Column('opera_id', Integer),  # foreign key
                    Column('performance_date', DateTime),
                    Column('performance_id', Integer),  # foreign key
                    Column('person_id', Integer),  # foreign key
                    Column('name', String),
                    Column('role', String)
                    )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(), data)


if __name__ == "__main__":
    main()
