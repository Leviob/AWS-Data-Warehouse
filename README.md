### Introduction

A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

I have built an ETL pipeline using AWS that extracts their data from S3, stages it in Redshift, and transforms data into a set of dimensional tables for their analytics team use for finding insights on what users are listening to. 

### Project Description

In this project, I have built an ETL pipeline for a database. The ETL pipeline is hosted on Amazon Redshift. Song and listening data is loaded from S3 into staging tables. These tables are then used to populate the fact and dimension tables of my database. 

My database is a star schema with `songplays` as its fact table, and `users`, `songs`, `artist`, and `time` as its dimension tables. These tables use distkeys and sortkeys to optimize performance for queries. this is accomplished by partitioning the data into logical slices for common queries. For example, in the `sonplays` table, data is partitioned by `user_id` so that each users listening data will be grouped together. The `songplays` table uses `artist_id` as the sortkey, so that information regarding individual artists listed to by particular users will be more efficient. 

### How to Run

In order to run this code, first a Redshift cluster must be launched and an IAM role must be configured. Then, `dwh.cfg` must be edited to  contain the correct information for connecting to the cluster such as the cluster endpoint, database name, database username, database password, IAM role, etc. Running `create_tables.py` will connect to the cluster and drop any previously created tables if there are any, and then create empty tables. Running `etl.py` will then copy data from S3 into the two staging tables `staging_events`, and `staging_songs`. These staging tables contain copies of the unprocessed data that are then used to populate the database tables. `etl.py` uses SQL INSERT statements to populate the fact table and 4 dimension tables using one or both of the staging tables. Hosting these staging tables on Redshift allows for efficient computation by reducing load on the ETL server.   

### File Descriptions

`sql_queries.py` - Contains all the SQL code used for dropping tables, creating tables, and inserting data into tables. The code within this file is run in`create_tables.py` and `etl.py`.

`create_tables.py` - Drops all tables if they exist and creates empty tables.

`etl.py` - Copies data from S3 to staging tables, and then uses staging tables to populate the database. 

### Example Queries 

Let's say we want a list of all the artists that each user listens to. The `songplays` table can be queried to give us this information. 

	SELECT sp.user_id, u.first_name, u.last_name, a.name AS artist_name
	FROM public.songplays AS sp
	JOIN public.users AS u
	ON sp.user_id = u.user_id
	JOIN public.artists AS a
	ON sp.artist_id = a.artist_id
	GROUP BY sp.user_id, u.first_name, u.last_name, a.name
	ORDER BY sp.user_id, a.name 
	LIMIT 10

The result is: 

user_id | first_name | last_name | artist_name
--- | --- | --- | ---
2 | Jizelle | Benjamin | Los Del Rio
2 | Jizelle | Benjamin | Shakira
2 | Jizelle | Benjamin | Shakira Featuring Wyclef Jean
6 | Cecilia | Owens | Dwight Yoakam
8 | Kaylee | Summers | Linkin Park
8 | Kaylee | Summers | The Mars Volta
8 | Kaylee | Summers | Yeah Yeah Yeahs
10 | Sylvie | Cruz | Lonnie Gordon
12 | Austin | Rosales | Kid Cudi
12 | Austin | Rosales | Kid Cudi / Kanye West / Common


As another example, say we wanted the locations where Sparkify has the most free tier users. The following code returns the locations with free users, sorted by the most free users first.

	SELECT COUNT(user_id) AS number_of_users, location
	FROM public.songplays
	WHERE level = 'free'
	GROUP BY location
	ORDER BY number_of_users DESC
	LIMIT 10

The result is: 

number_of_users | location
--- | ---
5 | New York-Newark-Jersey City, NY-NJ-PA
5 | New Haven-Milford, CT
4 | Houston-The Woodlands-Sugar Land, TX
3 | Phoenix-Mesa-Scottsdale, AZ
3 | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD
2 | Harrisburg-Carlisle, PA
2 | Klamath Falls, OR
2 | San Francisco-Oakland-Hayward, CA
2 | La Crosse-Onalaska, WI-MN
2 | Columbia, SC
