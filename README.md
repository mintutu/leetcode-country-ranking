# LeetCode Ranking
Crawling LeetCode Global Ranking and building a website to support to find the LeetCode ranking by country and username.

## Getting Started
Because LeetCode does not support to filter the ranking by country, so I've written some Python scripts to crawl global ranking data in LeetCode. It helps to search, filter by user name or countries.

Try to find your place and others in your country at: https://leetcode-country-ranking.herokuapp.com/

![Screenshot](https://i.ibb.co/RBd6z6x/Screen-Shot-2019-07-14-at-22-29-29.png)

I'm not good at frontend web development, so it would be great if you could help me to improve.

### Development at Local
In case, you want to build your own website. Run these steps at your local machine:
```
#Step 1: Run docker for the environment
docker-compose up -d

#Step 2: Download dependencies
pip3 install -r requirements.txt

#Step 3: Run heroku at local
heroku local

#Step 4: Test at http://localhost:5000/
```
### TODO
- Crawling LeetCode weekly contests
