# WiffleMaster
A webapp for keeping score, analyzing statistics, and managing players, teams, and leagues in wiffleball.

The goal of this project is to create an application where users can create and manage their own leagues, teams, and players. The app will be created using python and the flask webapp library, and the database will be managed using postgreSQL.

The goal is for each pitch to be logged into the database separately, so that the app produces detailed statistics for analytic purposes. Each at bat will have identifiers for the pitcher, batter, game, teams, and league in question so that data can be filtered and sorted.

This project will be used in the University of Helsinki course regarding databases and web development. The scope of the project is ambitious in relation to the requirements of the course, but the project is one I want to complete regardless, so I see this as a good opportunity to combine education with my own interests.

Currently, it is possible to register and log in as a user and create players, teams, and leagues. Players can be assigned to teams and moved from one team to another. A player can only be on one team at a time. Teams can be assigned to leagues, and can participate in several different leagues.

Games can now be logged and recorded into the database. The process is fully functional, and works according to the rules of wiffleball as intended. Note that this differs from baseball rules in some ways. For example, fielding errors and base stealing are not included. The user can decide how many innings are in a game, and what league (if any) the game is a part of.

The app now records everything into the database as is intended. The next step is to give users access to statistics based on the recorded data. For now, team pages show batting statistics for their players. The intention is to add pitching statistics to that, and make player pages show similar, but more detailed information. Additionally, league pages will display a standings table and statistics for league leaders. Also, a player search feature will be added. 

Installation instructions:

1. If you do not have python 3 installed, do so (https://www.python.org/downloads/).

2. In your terminal, navigate to the directory where you would like to install the app. When you clone the github repository, it will create a directory called "WiffleMaster".

```
$ mkdir app
$ cd app
```

3. Clone this repository into the folder.

```
$ git init
$ git clone https://github.com/uN1K0Rn86/WiffleMaster.git
```

4. Navigate to the WiffleMaster directory.

```
$ cd WiffleMaster
```

5. Create a virtual environment for the app so that you can contain all dependencies there:

```
$ python3 -m venv venv
```

6. Initialize the virtual environment:

```
$ source venv/bin/activate
```

7. Install dependencies:

```
(venv) $ pip install -r requirements.txt
```

8. Make sure you have PostgreSQL installed. If not, it can be found here https://www.postgresql.org/download/

9. Import the database schema into PSQL:

```
(venv) $ psql < schema.sql
```

10. Create a .env file into your app folder:

```
(venv) $ touch .env
```

11. Add the following lines into your .env file:

```
DATABASE_URL=postgresql:///{user}
SECRET_KEY={secret_key}
```

The database url will depend on the psql username. Type

```
(venv) $ psql
```

into your terminal so initialize PostgreSQL. The username should appear on the lower left:

```
username=#
```

The secret key must be unique. Generate your own secret key, for example with python:

```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
'18fd24bf6a2ad4dac04a33963db1c42f'
```

and copy it into your .env file (without the brackets).

12. Initialize the application:

```
(venv) $ flask run
```

13. You should get the following (or similar) message in your terminal:

```
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Navigate to the given address in your browser. The application is now ready for use.