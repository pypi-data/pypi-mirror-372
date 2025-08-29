from hgitaly.stub.repository_pb2 import RepositoryExistsRequest
from hgitaly.stub.shared_pb2 import Repository
from hgitaly.stub.repository_pb2_grpc import RepositoryServiceStub


def wait_server_accepts_connection(gitaly_channel, timeout=5):
    """Wait for a server using the Gitaly protocol to accept connections.

    wait for server to start enough that the address in bound
    Then the `wait_for_ready` option is there to ensure full readiness, but
    the client must at least receive something, e.g., the `CONNECTING` status
    for that to work.
    """
    repo_stub = RepositoryServiceStub(gitaly_channel)
    repo_stub.RepositoryExists(
        RepositoryExistsRequest(
            repository=Repository(
                relative_path="we/dont/care/waiting/for/any/connection",
                storage_name="default")
        ),
        timeout=timeout,
        wait_for_ready=True
    )
