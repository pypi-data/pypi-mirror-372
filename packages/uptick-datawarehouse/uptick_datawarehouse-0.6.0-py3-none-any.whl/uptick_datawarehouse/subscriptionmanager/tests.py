from unittest.mock import MagicMock, patch

from django.test import TestCase
from tickforge_client.models import Cluster, ServerTimezone, WorkspaceCluster
from tickforge_client.models import Workspace as TickforgeWorkspace

from app.core.tasks import sync_workspaces_from_tickforge
from uptick_datawarehouse.subscriptionmanager.models import (
    Workspace as DataWarehouseWorkspace,
)

mock_tickforge_workspaces = [
    TickforgeWorkspace(
        name="workspace1",
        customer="customer1",
        timezone=ServerTimezone.TZ_AU,  # type: ignore
        cluster=WorkspaceCluster(Cluster.PROD_MINUS_AU_MINUS_1),
        tags=["workforce", "customer", "production", "tz_au"],
    ),
    TickforgeWorkspace(
        name="workspace2",
        customer="customer2",
        timezone=ServerTimezone.TZ_GB,  # type: ignore
        cluster=WorkspaceCluster(Cluster.PROD_MINUS_GB_MINUS_1),
        tags=["workforce", "customer", "production", "tz_gb"],
    ),
    TickforgeWorkspace(
        name="workspace3",
        customer="customer3",
        timezone=ServerTimezone.TZ_NZ,  # type: ignore
        cluster=WorkspaceCluster(Cluster.PROD_MINUS_AU_MINUS_2),
        tags=["customer", "production", "tz_nz"],
    ),
]


@patch("boto3.client", return_value=MagicMock())
@patch("tickforge_client.get_access_token", return_value="A JWT Access Token")
@patch(
    "tickforge_client.api.workspaces_api.WorkspacesApi.list_workspaces_api_workspaces_get",
    return_value=mock_tickforge_workspaces,
)
class SyncWorkspacesFromTickforgeTestCase(TestCase):
    def assert_workspaces_equal(
        self,
        tickforge_workspace: TickforgeWorkspace,
        datawarehouse_workspace: DataWarehouseWorkspace,
    ) -> None:
        required_keys = ["name", "customer", "cluster", "tags"]

        tickforge_workspace_dict = tickforge_workspace.to_dict()
        datawarehouse_workspace_dict = datawarehouse_workspace.to_dict()
        tickforge_workspace_dict["cluster"] = tickforge_workspace_dict[
            "cluster"
        ].replace('"', "")
        datawarehouse_workspace_dict["cluster"] = datawarehouse_workspace_dict[
            "cluster"
        ].replace('"', "")
        for required_key in required_keys:
            self.assertEqual(
                tickforge_workspace_dict[required_key],
                datawarehouse_workspace_dict[required_key],
            )

    def test_sync(self, _, __, ___):
        datawarehouse_workspaces = DataWarehouseWorkspace.objects.all()
        self.assertEqual(len(datawarehouse_workspaces), 0)

        sync_workspaces_from_tickforge(None)

        datawarehouse_workspaces = DataWarehouseWorkspace.objects.all()
        self.assertEqual(len(datawarehouse_workspaces), 2)

        mock_tickforge_workspaces_tagged_workforce = list(
            filter(
                lambda mock_tickforge_workspace: "workforce"
                in mock_tickforge_workspace.tags,
                mock_tickforge_workspaces,
            )
        )
        for datawarehouse_workspace, tickforge_workspace in zip(
            datawarehouse_workspaces, mock_tickforge_workspaces_tagged_workforce
        ):
            self.assert_workspaces_equal(datawarehouse_workspace, tickforge_workspace)
