from src.main.models.HttpProblem import HttpProblem


class ValidationError(Exception):
    HTTP_PROBLEM_TYPE = "validation-error"

    def __init__(self, title="The request data was not valid.", detailed_validation_errors=[]):
        self.title = title
        self.detailed_validation_errors = detailed_validation_errors
        super().__init__(self.title)

    def to_http_problem(self):
        hp = HttpProblem(ValidationError.HTTP_PROBLEM_TYPE, self.title)
        hp.set_sub_errors(self.detailed_validation_errors)
        return hp
