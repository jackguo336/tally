# Tally

Tally is a command line tool for tracking team scores during a fitness
challenge. Fitness activities performed by users in a team are retrieved from
Strava and daily score are assigned based on a point system. The point system is provided in the section below.

## Point System

### User Points

For users, the points are calculated based on the total active time from all activities on a given day.

| Active Time  | Points Awarded                    |
|--------------|-----------------------------------|
| < 30 minutes | 0 points                          |
| ≥ 30 minutes | 5 points                          |
| ≥ 1 hour     | 7 points                          |
| ≥ 2 hours    | 8 points + 1 point per hour after |

#### Bonus Points

An additional 5 points are awarded to the user for each 7 consecutive days where the user is active (i.e. has received more than 0 points). The consecutive days cannot overlap, so at most 5 bonus points per week can be awarded to a user.

### Team Points

The team points for a given day are calculated by summing the points of all users in the team for that day.

#### Bonus Points

A team is awareded 5 additional points for a given day if all users in the team are active for that day (i.e. have received more than 0 points).

## Installation

### Prerequisites

- Python 3.10+
  - MacOS: install with `brew install python`
  - Windows: Download from https://www.python.org/downloads/windows/
- pipx
  - MacOS: install with `brew install pipx && pipx ensurepath`
  - Windows: `python3 -m pip install --user pipx && .\pipx.exe ensurepath`
- tkinter
  - MacOS: install with `brew install python-tk`
  - Windows: should be included with the Python installation
- Google Chrome
  - Download from https://www.google.com/chrome/

### Steps

1. Clone or download this repository
2. Install the command line tool
  a. MacOS: Run `chmod +x scripts/install.sh && scripts/install.sh`
  b. Windows: Run `scripts\install.ps1`
3. Run `tally` to start the tool

## How to use

1. Create clubs on Strava for each team. **Users in the club must set their activities to be viewable by other users of the club**. Verify this by checking that their activity appears in the club activity feed.
2. Create a Strava 'service account' and add it to each club. The account will be used to fetch activities from clubs.
3. Create a user registration spreadsheet from [user_team_registration_template.csv](./templates/user_team_registration_template.csv). It should contain the columns `team_name`, `team_id`, `user_name`, and `user_link`. Do not edit or move the column names.
4. Fill the spreadsheet with user and club (team) information, for example:

| team_name | team_id | user_name | user_link |
|-----------|---------|-----------|-----------|
| Team 1    | 532944  | John Doe  | https://www.strava.com/athletes/12432 |
| Team 2    | 234954  | Jane Doe  | https://www.strava.com/athletes/32543 |

5. Download the spreadsheet as a CSV file.
6. Run `tally` to start the tool.
7. When prompted, selected the `Configure challenge` option to configure a new challenge.

```
? Select an operation (Use arrow keys)
 » Configure challenge
   Track activities
   Calculate scores
   Delete all data
   Exit
```

8. Enter the name, start date and time zone for the challenge according to the prompts.
9. When asked to select a user list, choose the CSV file that was downloaded in the previous step.
10. Next, select the `Track activities` option to track new activities since the start of the challenge. It is recommended to run this command every week since activities older than 2 weeks may not be displayed in the club activity feed.
11. After activities have been tracked, select the `Calculate scores` option to calculate the team scores for the challenge. When prompted for the scoring end date, it is recommended to use yesterday's date since the scoring for today may be incomplete.
