from pydantic import BaseModel, Field

from ptsandbox.models import ComponentStatus, ComponentType


class SandboxComponentsResponse(BaseModel):
    """
    Information about system components
    """

    class Component(BaseModel):
        class Pod(BaseModel):
            name: str

            component_name: str = Field(alias="componentName")
            """
            Which component does it belong to
            """

            ready: bool
            """
            Ready status
            """

            node: str
            """
            The name of the node it is running on
            """

            restarts: int

            error_reason: str = Field(alias="errorReason")
            """
            The type of error, if any
            """

            error_message: str = Field(alias="errorMessage")
            """
            Error message, if any
            """

            uptime: int
            """
            Time elapsed since the container was launched (in seconds)
            """

            containers_running: int = Field(alias="containersRunning")
            """
            The number of working containers for a given hearth
            """

            containers_total: int = Field(alias="containersTotal")
            """
            The total number of containers specified in the pod specification (excluding init containers)
            """

        name: str

        total_pods: int = Field(alias="totalPods")
        """
        How many pods are there in total
        """

        ready_pods: int = Field(alias="readyPods")
        """
        How many are running
        """

        nodes: list[str]
        """
        The list of nodes running the component's pods
        """

        status: ComponentStatus
        """
        Component status
        """

        type: ComponentType
        """
        Component type
        """

        pods: list[Pod] = []
        """
        Список подов
        """

    components: list[Component] = []
