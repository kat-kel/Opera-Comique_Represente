from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from datetime import datetime


def main():
    engine = create_engine('sqlite:///bd.db')
    create_table_contribution(engine)
    create_table_user(engine)


def create_table_contribution(engine):
    table_name = 'contribution'
    metadata_obj = MetaData()
    opera_78 = datetime.strptime('1825-12-10', '%Y-%m-%d')
    opera_135 = datetime.strptime('1829-01-10', '%Y-%m-%d')
    opera_171 = datetime.strptime('1812-04-04', '%Y-%m-%d')
    data = [
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-08', '%Y-%m-%d'),
         'date_creation': opera_78,
         'opera_id': 78,
         'title': 'La Dame blanche',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()},
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-09', '%Y-%m-%d'),
         'date_creation':opera_78,
         'opera_id': 78,
         'title': 'La Dame blanche',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()},
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-10', '%Y-%m-%d'),
         'date_creation': opera_135,
         'opera_id': 135,
         'title': 'La Fiancée',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()},
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-10', '%Y-%m-%d'),
         'date_creation': opera_171,
         'opera_id': 171,
         'title': 'Jean de Paris',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()},
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-11', '%Y-%m-%d'),
         'date_creation': opera_135,
         'opera_id': 135,
         'title': 'La Fiancée',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()},
        {'source': 'Journal du Havre',
         'date_performance': datetime.strptime('1830-06-11', '%Y-%m-%d'),
         'date_creation': opera_171,
         'opera_id': 171,
         'title': 'Jean de Paris',
         'commune_id': 355,
         'commune_name': 'LE HAVRE',
         'user_id': 99,
         'timestamp': datetime.utcnow()}
    ]
    fields = Table(table_name, metadata_obj,
                   Column('id', Integer, primary_key=True),
                   Column('source', String(240)),
                   Column('date_performance', DateTime),
                   Column('date_creation', DateTime),
                   Column('opera_id', Integer),  # foreign key, opera.id_opera
                   Column('title', String(80)),
                   Column('commune_id', Integer),  # foreign key, communes.id_commune
                   Column('commune_name', String(80)),
                   Column('user_id', Integer),  # foreign key, user.id
                   Column('timestamp', DateTime, index=True)
                   )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert(), data)


def create_table_user(engine):
    table_name = 'user'
    metadata_obj = MetaData()
    fields = Table(table_name, metadata_obj,
                   Column('id', Integer, primary_key=True),
                   Column('username', String(64), index=True, unique=True),
                   Column('email', String(120), index=True, unique=True),
                   Column('password_hash', String(120)),
                   Column('first_name', String),
                   Column('last_name', String),
                   Column('about_me', String),
                   Column('last_seen', DateTime)
                   )
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    conn = engine.connect()
    conn.execute(fields.insert())


if __name__ == "__main__":
    main()
