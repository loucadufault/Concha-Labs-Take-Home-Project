from urllib.parse import urljoin


def set_resource_uri_header(request, response, relative_path_to_resource):
    response.headers["Location"] = urljoin(request.base_url, relative_path_to_resource)
