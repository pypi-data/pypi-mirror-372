import logging
import json

from r7_surcom_sdk.lib import constants, sdk_helpers, SurcomSDKException

LOG = logging.getLogger(constants.LOGGER_NAME)


def is_installed() -> bool:
    """
    Check if Docker is available in the system's PATH

    :return: True if Docker is available, False otherwise.
    :rtype: bool
    """
    try:

        cli_args = ["docker", "--version"]
        sdk_helpers.run_subprocess(cli_args)
        return True

    except SurcomSDKException:
        LOG.debug("Docker is not configured or accessible. Please ensure Docker is installed and running.")
        return False

    except Exception as e:
        LOG.debug(f"An unexpected error occurred while checking Docker installation: {e}")
        return False


def does_image_exist(
    docker_tag: str
) -> bool:
    """
    Check if the Docker image for the connector already exists

    :param docker_tag: The Docker tag for the connector
    :type docker_tag: str
    :return: True if the image exists, False otherwise
    :rtype: bool
    """

    try:
        cli_args = ["docker", "image", "inspect", docker_tag]
        sdk_helpers.run_subprocess(cli_args)
        return True
    except SurcomSDKException:
        return False


def delete_containers(
    docker_tag: str
):
    """
    Remove all Docker containers associated with a specific image tag.

    :param image_tag: The Docker image tag to filter containers by.
    :type image_tag: str
    """
    # Get all container IDs associated with the image tag
    cli_args = ["docker", "ps", "-a", "-q", "--filter", f"ancestor={docker_tag}"]
    result = sdk_helpers.run_subprocess(cli_args)

    if not result.stdout:
        LOG.debug(f"No containers found for image tag: {docker_tag}")
        return

    container_ids = result.stdout.decode("utf-8").strip().split("\n")

    # If there are containers, remove them
    if container_ids and container_ids[0]:
        cli_args = ["docker", "rm", "-f"] + container_ids
        sdk_helpers.run_subprocess(cli_args)
        LOG.debug(f"Removed containers associated with image tag: {docker_tag}")
    else:
        LOG.debug(f"No containers found for image tag: {docker_tag}")


def delete_image(
    docker_tag: str
):
    """
    Remove a Docker image by its tag.

    :param image_tag: The Docker image tag to remove.
    :type image_tag: str
    """
    if does_image_exist(docker_tag=docker_tag):
        cli_args = ["docker", "rmi", docker_tag]
        sdk_helpers.run_subprocess(cli_args)
        LOG.debug(f"Removed Docker image: {docker_tag}")


def get_exposed_ports(
    docker_tag: str
) -> list:
    """
    Get the exposed ports of a Docker image.

    :param docker_tag: The Docker image tag to inspect.
    :type docker_tag: str
    :return: A list of exposed ports.
    :rtype: list
    """
    try:
        cli_args = ["docker", "inspect", docker_tag, "--format={{json .Config.ExposedPorts}}"]
        result = sdk_helpers.run_subprocess(cli_args)
        ports = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        LOG.error(f"Failed to decode JSON from Docker inspect output: {e}")
        return []

    return list(ports.keys()) if ports else []
