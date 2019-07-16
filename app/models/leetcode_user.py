class User:
    def __init__(self, global_ranking, ranking, user_name, real_name, country_code, country_name, page):
        self.global_ranking = global_ranking
        self.ranking = ranking
        self.user_name = user_name
        self.real_name = real_name
        self.country_code = country_code
        self.country_name = country_name
        self.page = page

    def __str__(self):
        return "Global Ranking: {}\t UserName: {}\t realName: {}\t countryCode: {}\t countryName: {}".format(
            self.global_ranking, self.user_name, self.real_name, self.country_code, self.country_name)
