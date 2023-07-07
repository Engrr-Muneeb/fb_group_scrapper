class Filters:

    def __init__(self, string_to_search, include_users, exclude_users) -> None:
        self.string_to_search = string_to_search
        self.include_users = [k.strip() for k in include_users]
        self.exclude_users = [k.strip() for k in exclude_users]


    def IncludeUser(self, user_name):

        if not self.include_users:
            return True

        if user_name in self.include_users:
            return True

        return False

    def ExcludeUser(self, user_name):

        if not self.exclude_users:
            return False

        if user_name in self.exclude_users:
            return True

        return False

    def MatchText(self, text):
        if not self.string_to_search:
            return True
        if text is None:
            return False
        return True if self.string_to_search in text else False