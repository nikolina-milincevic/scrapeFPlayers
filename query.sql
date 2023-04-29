#DROP TABLE mydatabase.players;
SELECT * FROM mydatabase.players;

# query 1

ALTER TABLE mydatabase.players ADD COLUMN 
 AgeCategory VARCHAR(255)
 ;
UPDATE mydatabase.players SET
 AgeCategory = 'Young' WHERE age < 24 
 ;
UPDATE mydatabase.players SET
 AgeCategory = 'MidAge' WHERE age > 23 AND age < 33 
 ;
UPDATE mydatabase.players SET
 AgeCategory = 'Old' WHERE age > 32
 ;
 
ALTER TABLE mydatabase.players ADD COLUMN
 GoalsPerClubGame FLOAT
 ;
UPDATE mydatabase.players SET
 GoalsPerClubGame = 
	IF(number_of_apps > 0, goals/number_of_apps, NULL)
 ;

# query 2

SELECT AVG(age) as average_age FROM mydatabase.players;
SELECT AVG(number_of_apps) average_number_of_appearances
 FROM mydatabase.players
 ;
SELECT current_club, COUNT(*) as total_players
 FROM mydatabase.players
 GROUP BY current_club
 ;
 
 # query 3
 # first some maybe helful queries
SELECT name as rand_player
 FROM mydatabase.players WHERE 
  current_club = (SELECT current_club FROM 
  mydatabase.players ORDER BY RAND() LIMIT 1)
 ;
 SELECT name as rand_player
 FROM mydatabase.players WHERE 
  current_club = 'Liverpool'
 ;

#first solution
SELECT p1.name, COUNT(p2.name) FROM mydatabase.players p1
 JOIN mydatabase.players p2
 ON p1.position = p2.position 
 AND p2.date_of_birth > p1.date_of_birth
 AND p2.number_of_apps > p1.number_of_apps
 WHERE p1.name IN 
 (SELECT name FROM mydatabase.players WHERE 
  current_club = 'Liverpool') 
 GROUP BY p1.name
 ;
 #second solution
SELECT p1.name, COUNT(p2.name) FROM mydatabase.players p1
 JOIN mydatabase.players p2
 ON p1.player_id
 WHERE p1.position = p2.position AND
 p1.date_of_birth < p2.date_of_birth AND
 p1.number_of_apps < p2.number_of_apps AND
 p1.name in (SELECT name from mydatabase.players 
  where current_club = 'Liverpool')
 GROUP BY p1.name
 ;
  #just checking out:
  select count(*) from mydatabase.players
  where position = (select position from mydatabase.players
   where name = 'Mohamed Salah')
   and date_of_birth > (select date_of_birth from 
	 mydatabase.players where name = 'Mohamed Salah')
	and number_of_apps > (select number_of_apps from
    mydatabase.players where name = 'Mohamed Salah')
  ;
   select count(*) from mydatabase.players
  where position = (select position from mydatabase.players
   where name = 'Fábio Carvalho ')
   and date_of_birth > (select date_of_birth from 
	 mydatabase.players where name = 'Fábio Carvalho ')
	and number_of_apps > (select number_of_apps from
    mydatabase.players where name = 'Fábio Carvalho ')
  ;
  