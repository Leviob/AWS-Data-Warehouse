import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

LOG_DATA = config.get('S3', 'LOG_DATA')
LOG_JSONPATH = config.get('S3', 'LOG_JSONPATH')
SONG_DATA = config.get('S3', 'SONG_DATA')
IAM_ROLE = config.get('IAM_ROLE', 'ARN')

# DROP TABLES
staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES
staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS  staging_events (
    artist VARCHAR,
    auth VARCHAR,
    first_name VARCHAR,
    gender VARCHAR,
    item_in_session INTEGER,
    last_name VARCHAR,
    length FLOAT,
    level VARCHAR,
    location VARCHAR,
    method VARCHAR,
    page VARCHAR,
    registration BIGINT,
    session_id INTEGER,
    song VARCHAR,
    status INTEGER,
    ts TIMESTAMP,
    user_agent VARCHAR,
    user_id INTEGER);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs INTEGER,
    artist_id VARCHAR,
    artist_latitude VARCHAR, 
    artist_longitude VARCHAR,
    artist_location VARCHAR,
    artist_name VARCHAR,
    song_id VARCHAR,
    title VARCHAR,
    duration FLOAT,
    year int);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id int IDENTITY(0,1) PRIMARY KEY, 
    start_time TIMESTAMP NOT NULL, 
    user_id INTEGER distkey, 
    level VARCHAR NOT NULL, 
    song_id VARCHAR, 
    artist_id VARCHAR sortkey, 
    session_id INTEGER, 
    location VARCHAR, 
    user_agent VARCHAR);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, 
    first_name VARCHAR,
    last_name VARCHAR, 
    gender char,
    level VARCHAR(4) NOT NULL
);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs (
    song_id VARCHAR PRIMARY KEY,
    title VARCHAR,
    artist_id VARCHAR distkey,
    year INTEGER,
    duration decimal NOT NULL
);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR PRIMARY KEY distkey,
    name VARCHAR, 
    location VARCHAR, 
    latitude VARCHAR,
    longitude VARCHAR
);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time (
    start_time TIMESTAMP PRIMARY KEY distkey sortkey,
    hour INTEGER,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    year INTEGER,
    weekday INTEGER
);
""")

# STAGING TABLES
staging_events_copy = ("""
copy staging_events from {}
credentials 'aws_iam_role={}'
region 'us-west-2'
timeformat as 'epochmillisecs'
format as json {};
""").format(LOG_DATA, IAM_ROLE, LOG_JSONPATH)

staging_songs_copy = ("""
copy staging_songs from {}
credentials 'aws_iam_role={}'
region 'us-west-2' 
json 'auto';
""").format(SONG_DATA, IAM_ROLE)
    
# FINAL TABLES
songplay_table_insert = ("""
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT  se.ts AS start_time,
        se.user_id,
        se.level,
        ss.song_id,
        ss.artist_id,
        se.session_id,
        se.location,
        se.user_agent    
FROM staging_events AS se
JOIN staging_songs AS ss 
ON se.artist = ss.artist_name
AND se.song = ss.title
AND se.length = ss.duration
WHERE se.page = 'NextSong'
""")

user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT  DISTINCT user_id,
        first_name,
        last_name,
        gender,
        level
FROM staging_events
WHERE user_id IS NOT NULL
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT  DISTINCT song_id,
        title,
        artist_id,
        year,
        duration
FROM staging_songs
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT  DISTINCT artist_id,
        artist_name,
        artist_location,
        artist_latitude,
        artist_longitude
FROM staging_songs
""")

time_table_insert = ("""
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT ts AS start_time,
    DATE_PART(hour, ts) AS hour,
    DATE_PART(day, ts) AS day,
    DATE_PART(week, ts) AS week,
    DATE_PART(month, ts) AS month,
    DATE_PART(year, ts) AS year,
    DATE_PART(weekday, ts) AS weekday
FROM staging_events
""")

# QUERY LISTS
create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
