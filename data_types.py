class Common:

    def __init__(self, text, user, url, time):
        self.text = text
        self.user = user
        self.url = url
        self.time = time


class FBPost(Common):

    def __init__(self, text, user, url, time):
        super().__init__(text, user, url, time)
        self.comments = list()

    def AddComments(self, comments: list()):
        self.comments = comments


class Comment(Common):

    def __init__(self, text, user, url, time):
        super().__init__(text, user, url, time)
        self.post = None
        self.replies = list()

    def AddReply(self, reply):
        self.replies.append(reply)

    def SetParentPost(self, post):
        self.post = post


class Reply(Common):

    def __init__(self, text, user, url, time):
        super().__init__(text, user, url, time)
        self.comment = None

    def SetParentComment(self, comment):
        self.comment = comment