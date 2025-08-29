#
# This is an auto-generated file.  DO NOT EDIT!
#
# pylint: disable=line-too-long

from ansys.fluent.core.services.datamodel_se import (
    PyMenu,
    PyParameter,
    PyTextual,
    PyNumerical,
    PyDictionary,
    PyNamedObjectContainer,
    PyCommand,
    PyQuery,
    PyCommandArguments,
    PyTextualCommandArgumentsSubItem,
    PyNumericalCommandArgumentsSubItem,
    PyDictionaryCommandArgumentsSubItem,
    PyParameterCommandArgumentsSubItem,
    PySingletonCommandArgumentsSubItem
)


class Root(PyMenu):
    """
    Singleton Root.
    """
    def __init__(self, service, rules, path):
        self.TaskObject = self.__class__.TaskObject(service, rules, path + [("TaskObject", "")])
        self.Workflow = self.__class__.Workflow(service, rules, path + [("Workflow", "")])
        self.CreateCompositeTask = self.__class__.CreateCompositeTask(service, rules, "CreateCompositeTask", path)
        self.CreateNewWorkflow = self.__class__.CreateNewWorkflow(service, rules, "CreateNewWorkflow", path)
        self.DeleteTasks = self.__class__.DeleteTasks(service, rules, "DeleteTasks", path)
        self.InitializeWorkflow = self.__class__.InitializeWorkflow(service, rules, "InitializeWorkflow", path)
        self.InsertNewTask = self.__class__.InsertNewTask(service, rules, "InsertNewTask", path)
        self.LoadState = self.__class__.LoadState(service, rules, "LoadState", path)
        self.LoadWorkflow = self.__class__.LoadWorkflow(service, rules, "LoadWorkflow", path)
        self.ResetWorkflow = self.__class__.ResetWorkflow(service, rules, "ResetWorkflow", path)
        self.SaveWorkflow = self.__class__.SaveWorkflow(service, rules, "SaveWorkflow", path)
        super().__init__(service, rules, path)

    class TaskObject(PyNamedObjectContainer):
        """
        .
        """
        class _TaskObject(PyMenu):
            """
            Singleton _TaskObject.
            """
            def __init__(self, service, rules, path):
                self.Arguments = self.__class__.Arguments(service, rules, path + [("Arguments", "")])
                self.CommandName = self.__class__.CommandName(service, rules, path + [("CommandName", "")])
                self.Errors = self.__class__.Errors(service, rules, path + [("Errors", "")])
                self.InactiveTaskList = self.__class__.InactiveTaskList(service, rules, path + [("InactiveTaskList", "")])
                self.ObjectPath = self.__class__.ObjectPath(service, rules, path + [("ObjectPath", "")])
                self.State = self.__class__.State(service, rules, path + [("State", "")])
                self.TaskList = self.__class__.TaskList(service, rules, path + [("TaskList", "")])
                self.TaskType = self.__class__.TaskType(service, rules, path + [("TaskType", "")])
                self.Warnings = self.__class__.Warnings(service, rules, path + [("Warnings", "")])
                self._name_ = self.__class__._name_(service, rules, path + [("_name_", "")])
                self.AddChildAndUpdate = self.__class__.AddChildAndUpdate(service, rules, "AddChildAndUpdate", path)
                self.AddChildToTask = self.__class__.AddChildToTask(service, rules, "AddChildToTask", path)
                self.Execute = self.__class__.Execute(service, rules, "Execute", path)
                self.ExecuteUpstreamNonExecutedAndThisTask = self.__class__.ExecuteUpstreamNonExecutedAndThisTask(service, rules, "ExecuteUpstreamNonExecutedAndThisTask", path)
                self.ForceUptoDate = self.__class__.ForceUptoDate(service, rules, "ForceUptoDate", path)
                self.GetNextPossibleTasks = self.__class__.GetNextPossibleTasks(service, rules, "GetNextPossibleTasks", path)
                self.InsertCompositeChildTask = self.__class__.InsertCompositeChildTask(service, rules, "InsertCompositeChildTask", path)
                self.InsertCompoundChildTask = self.__class__.InsertCompoundChildTask(service, rules, "InsertCompoundChildTask", path)
                self.InsertNextTask = self.__class__.InsertNextTask(service, rules, "InsertNextTask", path)
                self.Rename = self.__class__.Rename(service, rules, "Rename", path)
                self.Revert = self.__class__.Revert(service, rules, "Revert", path)
                self.SetAsCurrent = self.__class__.SetAsCurrent(service, rules, "SetAsCurrent", path)
                self.UpdateChildTasks = self.__class__.UpdateChildTasks(service, rules, "UpdateChildTasks", path)
                super().__init__(service, rules, path)

            class Arguments(PyDictionary):
                """
                Parameter Arguments of value type dict[str, Any].
                """
                pass

            class CommandName(PyTextual):
                """
                Parameter CommandName of value type str.
                """
                pass

            class Errors(PyTextual):
                """
                Parameter Errors of value type list[str].
                """
                pass

            class InactiveTaskList(PyTextual):
                """
                Parameter InactiveTaskList of value type list[str].
                """
                pass

            class ObjectPath(PyTextual):
                """
                Parameter ObjectPath of value type str.
                """
                pass

            class State(PyTextual):
                """
                Parameter State of value type str.
                """
                pass

            class TaskList(PyTextual):
                """
                Parameter TaskList of value type list[str].
                """
                pass

            class TaskType(PyTextual):
                """
                Parameter TaskType of value type str.
                """
                pass

            class Warnings(PyTextual):
                """
                Parameter Warnings of value type list[str].
                """
                pass

            class _name_(PyTextual):
                """
                Parameter _name_ of value type str.
                """
                pass

            class AddChildAndUpdate(PyCommand):
                """
                Command AddChildAndUpdate.

                Parameters
                ----------
                DeferUpdate : bool

                Returns
                -------
                bool
                """
                class _AddChildAndUpdateCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.DeferUpdate = self._DeferUpdate(self, "DeferUpdate", service, rules, path)

                    class _DeferUpdate(PyParameterCommandArgumentsSubItem):
                        """
                        Argument DeferUpdate.
                        """

                def create_instance(self) -> _AddChildAndUpdateCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._AddChildAndUpdateCommandArguments(*args)

            class AddChildToTask(PyCommand):
                """
                Command AddChildToTask.


                Returns
                -------
                bool
                """
                class _AddChildToTaskCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _AddChildToTaskCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._AddChildToTaskCommandArguments(*args)

            class Execute(PyCommand):
                """
                Command Execute.

                Parameters
                ----------
                Force : bool

                Returns
                -------
                bool
                """
                class _ExecuteCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.Force = self._Force(self, "Force", service, rules, path)

                    class _Force(PyParameterCommandArgumentsSubItem):
                        """
                        Argument Force.
                        """

                def create_instance(self) -> _ExecuteCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._ExecuteCommandArguments(*args)

            class ExecuteUpstreamNonExecutedAndThisTask(PyCommand):
                """
                Command ExecuteUpstreamNonExecutedAndThisTask.


                Returns
                -------
                bool
                """
                class _ExecuteUpstreamNonExecutedAndThisTaskCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _ExecuteUpstreamNonExecutedAndThisTaskCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._ExecuteUpstreamNonExecutedAndThisTaskCommandArguments(*args)

            class ForceUptoDate(PyCommand):
                """
                Command ForceUptoDate.


                Returns
                -------
                bool
                """
                class _ForceUptoDateCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _ForceUptoDateCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._ForceUptoDateCommandArguments(*args)

            class GetNextPossibleTasks(PyCommand):
                """
                Command GetNextPossibleTasks.


                Returns
                -------
                bool
                """
                class _GetNextPossibleTasksCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _GetNextPossibleTasksCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._GetNextPossibleTasksCommandArguments(*args)

            class InsertCompositeChildTask(PyCommand):
                """
                Command InsertCompositeChildTask.

                Parameters
                ----------
                CommandName : str

                Returns
                -------
                bool
                """
                class _InsertCompositeChildTaskCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.CommandName = self._CommandName(self, "CommandName", service, rules, path)

                    class _CommandName(PyTextualCommandArgumentsSubItem):
                        """
                        Argument CommandName.
                        """

                def create_instance(self) -> _InsertCompositeChildTaskCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._InsertCompositeChildTaskCommandArguments(*args)

            class InsertCompoundChildTask(PyCommand):
                """
                Command InsertCompoundChildTask.


                Returns
                -------
                bool
                """
                class _InsertCompoundChildTaskCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _InsertCompoundChildTaskCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._InsertCompoundChildTaskCommandArguments(*args)

            class InsertNextTask(PyCommand):
                """
                Command InsertNextTask.

                Parameters
                ----------
                CommandName : str
                Select : bool

                Returns
                -------
                bool
                """
                class _InsertNextTaskCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.CommandName = self._CommandName(self, "CommandName", service, rules, path)
                        self.Select = self._Select(self, "Select", service, rules, path)

                    class _CommandName(PyTextualCommandArgumentsSubItem):
                        """
                        Argument CommandName.
                        """

                    class _Select(PyParameterCommandArgumentsSubItem):
                        """
                        Argument Select.
                        """

                def create_instance(self) -> _InsertNextTaskCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._InsertNextTaskCommandArguments(*args)

            class Rename(PyCommand):
                """
                Command Rename.

                Parameters
                ----------
                NewName : str

                Returns
                -------
                bool
                """
                class _RenameCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.NewName = self._NewName(self, "NewName", service, rules, path)

                    class _NewName(PyTextualCommandArgumentsSubItem):
                        """
                        Argument NewName.
                        """

                def create_instance(self) -> _RenameCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._RenameCommandArguments(*args)

            class Revert(PyCommand):
                """
                Command Revert.


                Returns
                -------
                bool
                """
                class _RevertCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _RevertCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._RevertCommandArguments(*args)

            class SetAsCurrent(PyCommand):
                """
                Command SetAsCurrent.


                Returns
                -------
                bool
                """
                class _SetAsCurrentCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)

                def create_instance(self) -> _SetAsCurrentCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._SetAsCurrentCommandArguments(*args)

            class UpdateChildTasks(PyCommand):
                """
                Command UpdateChildTasks.

                Parameters
                ----------
                SetupTypeChanged : bool

                Returns
                -------
                bool
                """
                class _UpdateChildTasksCommandArguments(PyCommandArguments):
                    def __init__(self, service, rules, command, path, id):
                        super().__init__(service, rules, command, path, id)
                        self.SetupTypeChanged = self._SetupTypeChanged(self, "SetupTypeChanged", service, rules, path)

                    class _SetupTypeChanged(PyParameterCommandArgumentsSubItem):
                        """
                        Argument SetupTypeChanged.
                        """

                def create_instance(self) -> _UpdateChildTasksCommandArguments:
                    args = self._get_create_instance_args()
                    if args is not None:
                        return self._UpdateChildTasksCommandArguments(*args)

        def __getitem__(self, key: str) -> _TaskObject:
            return super().__getitem__(key)

    class Workflow(PyMenu):
        """
        Singleton Workflow.
        """
        def __init__(self, service, rules, path):
            self.CurrentTask = self.__class__.CurrentTask(service, rules, path + [("CurrentTask", "")])
            self.TaskList = self.__class__.TaskList(service, rules, path + [("TaskList", "")])
            super().__init__(service, rules, path)

        class CurrentTask(PyTextual):
            """
            Parameter CurrentTask of value type str.
            """
            pass

        class TaskList(PyTextual):
            """
            Parameter TaskList of value type list[str].
            """
            pass

    class CreateCompositeTask(PyCommand):
        """
        Command CreateCompositeTask.

        Parameters
        ----------
        ListOfTasks : list[str]

        Returns
        -------
        bool
        """
        class _CreateCompositeTaskCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.ListOfTasks = self._ListOfTasks(self, "ListOfTasks", service, rules, path)

            class _ListOfTasks(PyTextualCommandArgumentsSubItem):
                """
                Argument ListOfTasks.
                """

        def create_instance(self) -> _CreateCompositeTaskCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._CreateCompositeTaskCommandArguments(*args)

    class CreateNewWorkflow(PyCommand):
        """
        Command CreateNewWorkflow.


        Returns
        -------
        bool
        """
        class _CreateNewWorkflowCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)

        def create_instance(self) -> _CreateNewWorkflowCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._CreateNewWorkflowCommandArguments(*args)

    class DeleteTasks(PyCommand):
        """
        Command DeleteTasks.

        Parameters
        ----------
        ListOfTasks : list[str]

        Returns
        -------
        bool
        """
        class _DeleteTasksCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.ListOfTasks = self._ListOfTasks(self, "ListOfTasks", service, rules, path)

            class _ListOfTasks(PyTextualCommandArgumentsSubItem):
                """
                Argument ListOfTasks.
                """

        def create_instance(self) -> _DeleteTasksCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._DeleteTasksCommandArguments(*args)

    class InitializeWorkflow(PyCommand):
        """
        Command InitializeWorkflow.

        Parameters
        ----------
        WorkflowType : str

        Returns
        -------
        bool
        """
        class _InitializeWorkflowCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.WorkflowType = self._WorkflowType(self, "WorkflowType", service, rules, path)

            class _WorkflowType(PyTextualCommandArgumentsSubItem):
                """
                Argument WorkflowType.
                """

        def create_instance(self) -> _InitializeWorkflowCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._InitializeWorkflowCommandArguments(*args)

    class InsertNewTask(PyCommand):
        """
        Command InsertNewTask.

        Parameters
        ----------
        CommandName : str

        Returns
        -------
        bool
        """
        class _InsertNewTaskCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.CommandName = self._CommandName(self, "CommandName", service, rules, path)

            class _CommandName(PyTextualCommandArgumentsSubItem):
                """
                Argument CommandName.
                """

        def create_instance(self) -> _InsertNewTaskCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._InsertNewTaskCommandArguments(*args)

    class LoadState(PyCommand):
        """
        Command LoadState.

        Parameters
        ----------
        ListOfRoots : list[str]

        Returns
        -------
        bool
        """
        class _LoadStateCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.ListOfRoots = self._ListOfRoots(self, "ListOfRoots", service, rules, path)

            class _ListOfRoots(PyTextualCommandArgumentsSubItem):
                """
                Argument ListOfRoots.
                """

        def create_instance(self) -> _LoadStateCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._LoadStateCommandArguments(*args)

    class LoadWorkflow(PyCommand):
        """
        Command LoadWorkflow.

        Parameters
        ----------
        FilePath : str

        Returns
        -------
        bool
        """
        class _LoadWorkflowCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.FilePath = self._FilePath(self, "FilePath", service, rules, path)

            class _FilePath(PyTextualCommandArgumentsSubItem):
                """
                Argument FilePath.
                """

        def create_instance(self) -> _LoadWorkflowCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._LoadWorkflowCommandArguments(*args)

    class ResetWorkflow(PyCommand):
        """
        Command ResetWorkflow.


        Returns
        -------
        bool
        """
        class _ResetWorkflowCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)

        def create_instance(self) -> _ResetWorkflowCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._ResetWorkflowCommandArguments(*args)

    class SaveWorkflow(PyCommand):
        """
        Command SaveWorkflow.

        Parameters
        ----------
        FilePath : str

        Returns
        -------
        bool
        """
        class _SaveWorkflowCommandArguments(PyCommandArguments):
            def __init__(self, service, rules, command, path, id):
                super().__init__(service, rules, command, path, id)
                self.FilePath = self._FilePath(self, "FilePath", service, rules, path)

            class _FilePath(PyTextualCommandArgumentsSubItem):
                """
                Argument FilePath.
                """

        def create_instance(self) -> _SaveWorkflowCommandArguments:
            args = self._get_create_instance_args()
            if args is not None:
                return self._SaveWorkflowCommandArguments(*args)

