from typing import List, Callable


class DeletableResource:
    """
    A DeletableResource represents a named resource that can be deleted.
    """

    name: str
    delete: Callable

    def __init__(self, name: str, delete: Callable):
        """
        Creates a deletable resource, to be passed to DeletableResourceContainer.add_resource().
        :param name: The name of the resource, to be used for logging.
        :param delete: The callback to delete the resource.
        """
        self.name = name
        self.delete = delete


class DeletableResourceContainer:
    """
    A DeletableResourceContainer is intended to be used during async workflows that create multiple resources.

    How to use: For each resource that you successfully create, call add_resource. When failing to create a resource,
    call delete_resources to dispose of previously created resources.
    """

    resources: List[DeletableResource]

    def __init__(self, log):
        self.resources = []
        self.log = log

    def add_resource(self, resource: DeletableResource):
        """
        Adds a deletable resource. Call this right after successfully creating a resource.
        """
        self.resources.append(resource)

    def clear(self):
        """
        Clears the list of deletable resources. Call this after all resources have been created successfully.
        """
        self.resources.clear()

    async def delete_all(self):
        """
        Deletes all registered resources, sequentially in the order they were registered.

        This does not account for resources that require asynchronous deletions (i.e., polling to confirm deletion).
        """
        for resource in self.resources:
            try:
                self.log.info(f"Deleting resource '{resource.name}'...")
                await resource.delete()
                self.log.info(f"Successfully deleted resource '{resource.name}'.")
            except Exception as ex:
                self.log.error(f"Error cleaning up resource '{resource.name}' : {ex}")
