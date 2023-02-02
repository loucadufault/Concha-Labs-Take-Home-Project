from .UserInfo import UserInfo
from .Audio import Audio

from .HttpProblem import HttpProblem

"""Represents various API models of the server.

Entity models such as UserInfo and Audio are dataclasses meant to represent domain entities of this application in 
transit between layers during handling of a request. They correspond to those fields from the schema of database 
entities that are meant to be supplied in input (less the 'id', which is created automatically).
They include internal fields (e.g. id), therefore the request data expected to create instances of these models is a 
subset of the complete model.

The HttpProblem model represents data for a failed response representing the problem, to be used in conjunction with the HTTP status code.
"""