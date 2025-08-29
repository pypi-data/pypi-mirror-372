import pytest

from kognic.io.client import KognicIOClient

ORGANIZATION_ID = 1


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default="development", help="env can be staging or development")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def organization_id():
    return ORGANIZATION_ID


@pytest.fixture(autouse=True, scope="session")
def client(env: str, organization_id: int) -> KognicIOClient:
    """
    Factory to use the IO Client
    """

    if env == "development" or env is None:
        auth_host = "http://kognic.test:8001"
        workspace_host = "http://kognic.test:8030"
        input_api_host = "http://kognic.test:8010"
        order_execution_api_host = "http://kognic.test:8011"
        annotation_integration_api_host = "http://kognic.test:8034"
        workspace_id = "<change this for the real workspace in dev>"
    elif env == "staging":
        auth_host = "https://auth.staging.kognic.com"
        workspace_host = "https://workspace.staging.kognic.com"
        input_api_host = "https://input.staging.kognic.com"
        order_execution_api_host = "https://order-execution.staging.kognic.com"
        annotation_integration_api_host = "https://annotation-integration.staging.kognic.com"
        workspace_id = "557ca28f-c405-4dd3-925f-ee853d858e4b"
    else:
        raise RuntimeError(f"ENV: {env} is not supported")
    return KognicIOClient(
        auth=None,
        auth_host=auth_host,
        host=input_api_host,
        order_execution_api_host=order_execution_api_host,
        annotation_integration_api_host=annotation_integration_api_host,
        workspace_api_host=workspace_host,
        client_organization_id=organization_id,
        write_workspace_id=workspace_id,
    )


@pytest.fixture(autouse=True)
def uri_for_external_image():
    return "s3://jesper-test-chain-of-trust-2/zod/000000/camera_front_blur/000000_quebec_2022-02-14T13:23:32_140954Z.jpg"


@pytest.fixture(autouse=True)
def uri_for_external_lidar():
    return "s3://jesper-test-chain-of-trust-2/zod/000000/lidar_velodyne/000000_quebec_2022-02-14T13:23:32_251875Z.csv"


@pytest.fixture(autouse=True)
def uri_for_external_imu():
    return "s3://jesper-test-chain-of-trust-2/zod/000000/dummy_imu.json"


@pytest.fixture(autouse=True)
def uri_for_external_ol():
    return "s3://jesper-test-chain-of-trust-2/jespers-external-ol.json"


@pytest.fixture(autouse=True)
def existing_pre_annotation_uuid():
    """
    Fixture UUID for an existing staging pre-annotation.
    """
    return "d4c6de15-974c-4130-b47c-310e4bb668dd"


@pytest.fixture(autouse=True)
def existing_lacs_scene_uuid():
    """
    Fixture UUID for some existing staging LACS scene. It has both pre-annotations and inputs.
    """
    return "81388ad7-be4a-42a8-9562-86f766e0aa97"
