# leetcode-country-ranking
Craw LeetCode global ranking and supports to filter by country

## Getting Started
Because LeetCode does not support to filter the ranking by country, so I write some small scripts to craw global ranking data in LeetCode. It helps to search, filter by user name or countries.
Try to find your place and others in your country at: https://leetcode-country-ranking.herokuapp.com/

![Screenshot](https://i.ibb.co/RBd6z6x/Screen-Shot-2019-07-14-at-22-29-29.png)

### Develop at Local
In case, you want to build your own crawler. Run these steps at your local machine:
```
#Step 1: Run docker for the environment
docker-compose up -d

#Step 2: Set up the environment variables
export MONGODB_URI="mongodb://root:example@localhost:27017/"

#Step 3: Download dependencies
pip3 install -r requirements.txt

#Step 3: Run heroku at local
heroku local

#Step 4: Test at http://localhost:5000/
```
