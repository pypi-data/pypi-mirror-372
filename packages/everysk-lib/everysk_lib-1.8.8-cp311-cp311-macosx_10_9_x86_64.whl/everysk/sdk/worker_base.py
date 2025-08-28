###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.object import BaseDict


###############################################################################
#   WorkerBase Class Implementation
###############################################################################
class WorkerBase(BaseDict):

    workspace: str = None
    script_inputs: BaseDict = None
    inputs_info: BaseDict = None
    worker_type: str = None
    parallel_info: BaseDict = None
    worker_id: str = None
    workflow_id: str = None
    workflow_execution_id: str = None

    def __init__(self, args: BaseDict = Undefined, **kwargs):
        if args is Undefined:
            args = {}
        kwargs.update(args)
        super().__init__(**kwargs)

    def handle_inputs(self) -> None:
        if self.script_inputs:
            for key, value in self.script_inputs.items():
                setattr(self, key, value)

    def handle_tasks(self) -> None:
        raise NotImplementedError()

    def handle_outputs(self) -> BaseDict:
        raise NotImplementedError()

    def run(self) -> BaseDict:
        self.handle_inputs()
        self.handle_tasks()
        return self.handle_outputs()
