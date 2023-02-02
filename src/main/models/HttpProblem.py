class HttpProblem:
    class SubError:
        def __init__(self, **kwargs):
            if "detail" in kwargs:
                self.detail = kwargs["detail"]
            self.extensions = dict()
            self.extensions.update(kwargs)

        def serialize(self):
            s = dict(self.extensions)
            s["detail"] = self.detail
            return s

    def __init__(self, ptype, title, **kwargs):
        self.type = ptype
        self.title = title
        self.extensions = dict()
        self.extensions.update(**kwargs)
        self.sub_errors = []

    def set_sub_errors(self, sub_errors):
        self.sub_errors = [HttpProblem.SubError(**sub_error) for sub_error in sub_errors]

    def serialize(self):
        s = dict(self.extensions)
        s["type"] = self.type
        s["title"] = self.title
        if len(self.sub_errors) > 0:
            s["errors"] = [sub_error.serialize() for sub_error in self.sub_errors]
        return s
