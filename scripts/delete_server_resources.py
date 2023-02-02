from requests_toolbelt import sessions
import click


def get_http_session(server_url):
    return sessions.BaseUrlSession(
        base_url=server_url)


def extract_resource_ids(res):
    result = []
    for resource in res.json():
        if "id" in resource:
            result.append(resource["id"])
        elif "session_id" in resource:
            result.append(resource["session_id"])

    return result


@click.command()
@click.option("--server_url", prompt="The server against which to make the requests")
@click.option("--endpoint", prompt="The endpoint for the resources to delete, namely 'accounts' or 'audios'")
def delete_all_resources(server_url, endpoint):
    s = get_http_session(server_url)
    res = s.get(f"/{endpoint}")
    resource_ids = extract_resource_ids(res)
    if len(resource_ids) == 0:
        click.echo(f"No resources found at '{endpoint}' endpoint to delete against '{server_url}'")
        return

    click.echo(f"Deleting {len(resource_ids)} resources against '{server_url}'. This could take a few minutes...")
    for resource_id in resource_ids:
        click.echo(f"Deleting resource '{endpoint}/{resource_id}'")
        s.delete(f"/{endpoint}/{resource_id}")


if __name__ == "__main__":
    delete_all_resources()
