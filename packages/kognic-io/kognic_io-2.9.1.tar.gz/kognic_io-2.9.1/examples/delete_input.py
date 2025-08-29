from kognic.io.client import KognicIOClient


def run(client: KognicIOClient, input_uuid: str) -> None:
    print("Deleting input...")
    return client.input.delete_input(input_uuid=input_uuid)


if __name__ == "__main__":
    client = KognicIOClient()

    input_uuid = "Input-identifier"
    run(client, input_uuid)
