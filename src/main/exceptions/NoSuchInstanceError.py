from src.main.models import HttpProblem


class NoSuchInstanceError(Exception):
    HTTP_PROBLEM_TYPE = "no-such-instance-error"

    """No such instance of the requested data entity was found."""
    def __init__(self, title="No such instance of the entity was found."):
        self.title = title
        super().__init__(self.title)

    def to_http_problem(self):
        return HttpProblem(NoSuchInstanceError.HTTP_PROBLEM_TYPE, self.title)
