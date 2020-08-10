import os
from app import app
from scout_apm.flask import ScoutApm

ScoutApm(app)

# Scout settings
app.config["SCOUT_MONITOR"] = os.getenv("SCOUT_MONITOR", "false")
app.config["SCOUT_KEY"] = os.getenv("SCOUT_KEY", "")
app.config["SCOUT_NAME"] = "leetcode-country-ranking"

if __name__ == '__main__':
    app.run()