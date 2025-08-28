import contextvars
import io
import os
import sys
import zipfile
import signal

import uuid
import yaml
import cloudpickle as pickle

from datetime import timedelta
from typing import Any, Callable, Dict, Generic, List, Optional, ParamSpec, Tuple, TypeVar, Union
from .utils import LazyArgs, _poll_batch_for_results, create_grpc_channel
from .results import ResultHandle, MultiResultHandle
from .materialize import Materialize, _create_zip_from_directory

from armonik.client import ArmoniKTasks, ArmoniKResults, ArmoniKSessions, ArmoniKEvents
from armonik.common import TaskOptions, TaskDefinition, Result, batched
from armonik.worker import TaskHandler 

_CURRENT_PYMONIK: contextvars.ContextVar[Optional["Pymonik"]] = contextvars.ContextVar(
    "_CURRENT_PYMONIK", default=None
)

P_Args = ParamSpec("P_Args")
R_Type = TypeVar("R_Type")

U_Obj = TypeVar("U_Obj") # For single object in put
V_Obj = TypeVar("V_Obj") # For type of objects in a list for put_many

class Task(Generic[P_Args, R_Type]):
    """A wrapper for a function that can be executed as an ArmoniK task."""

    def __init__(
        self, func: Callable, require_context: bool = False, func_name: str = None,        task_options: Optional[TaskOptions] = None

    ):
        self.func: Callable[P_Args, R_Type] = func
        self.func_name = func_name or func.__name__
        self.require_context = require_context
        self.task_options = task_options


    def _merge_task_options(
        self, 
        pymonik_instance: "Pymonik",
        task_options: Optional[TaskOptions] = None,
        pmk_kwargs: Dict[str, Any] = None
    ) -> TaskOptions:
        """Merge task options from different sources with proper precedence."""
        pmk_kwargs = pmk_kwargs or {}
        # Start with Pymonik instance defaults
        base_options = pymonik_instance.task_options
        
        # Create a dictionary to build the merged options
        merged_attrs = {
            'max_duration': base_options.max_duration,
            'priority': base_options.priority,
            'max_retries': base_options.max_retries,
            'partition_id': base_options.partition_id,
            'options' : base_options.options
        }
        
        # Apply task decorator options if they exist
        if self.task_options:
            if self.task_options.max_duration is not None:
                merged_attrs['max_duration'] = self.task_options.max_duration
            if self.task_options.priority is not None:
                merged_attrs['priority'] = self.task_options.priority
            if self.task_options.max_retries is not None:
                merged_attrs['max_retries'] = self.task_options.max_retries
            if self.task_options.partition_id is not None:
                merged_attrs['partition_id'] = self.task_options.partition_id
            if self.task_options.options is not None:
                merged_attrs['options'] = self.task_options.options
        
        # Apply invocation-specific task options
        if task_options:
            if task_options.max_duration is not None:
                merged_attrs['max_duration'] = task_options.max_duration
            if task_options.priority is not None:
                merged_attrs['priority'] = task_options.priority
            if task_options.max_retries is not None:
                merged_attrs['max_retries'] = task_options.max_retries
            if task_options.partition_id is not None:
                merged_attrs['partition_id'] = task_options.partition_id
            if task_options.options is not None:
                merged_attrs['options'] = task_options.options
            
        # Apply pmk_ prefixed options
        for key, value in pmk_kwargs.items():
            if key.startswith('pmk_'):
                option_name = key[4:]  # Remove 'pmk_' prefix
                if option_name == 'max_duration':
                    # Handle duration conversion if needed
                    if isinstance(value, (int, float)):
                        merged_attrs['max_duration'] = timedelta(seconds=value)
                    elif isinstance(value, timedelta):
                        merged_attrs['max_duration'] = value
                else:
                    merged_attrs[option_name] = value
        
        return TaskOptions(
            max_duration=merged_attrs['max_duration'],
            priority=merged_attrs['priority'],
            max_retries=merged_attrs['max_retries'],
            partition_id=merged_attrs['partition_id'],
            options=merged_attrs['options']
        )

    # TODO: repeat invocations for parameter-less functions my_function.invoke(repeat=5)
    def invoke(
        self, *args, pymonik: Optional["Pymonik"] = None, delegate=False, task_options: Optional[TaskOptions] = None, **kwargs
    ) -> ResultHandle[R_Type]:
        """Invoke the task with the given arguments."""

        pmk_kwargs = {k: v for k, v in kwargs.items() if k.startswith('pmk_')}
        regular_kwargs = {k: v for k, v in kwargs.items() if not k.startswith('pmk_')}


        # Handle the case of a single task
        if pymonik is None:
            pymonik = _CURRENT_PYMONIK.get(None)
            if pymonik is None:
                raise RuntimeError(
                    "No active PymoniK instance found. Please create one and pass it in or use the context manager."
                )
                
        # I'm using the 'pmk_' prefix to avoid potential naming conflicts.
        merged_task_options = self._merge_task_options(pymonik, task_options, pmk_kwargs)
        
        if len(args) == 0:
            results = self._invoke_multiple([(Pymonik.NoInput,)], pymonik, delegate, merged_task_options)
            return results[0]
        results: List[ResultHandle[R_Type]] = self._invoke_multiple([args], pymonik, delegate, merged_task_options, additional_kwargs=regular_kwargs if regular_kwargs != {} else None)
        return results[0]

    def map_invoke(
        self,
        args_list: List[Tuple],
        pymonik: Optional["Pymonik"] = None,
        delegate=False,
        task_options: Optional[TaskOptions] = None,
        **kwargs
    ) -> MultiResultHandle:
        """Invoke the task with the given arguments and return a MultiResultHandle."""
        
        pmk_kwargs = {k: v for k, v in kwargs.items() if k.startswith('pmk_')}
        
        if pymonik is None:
            pymonik = _CURRENT_PYMONIK.get(None)
            if pymonik is None:
                raise RuntimeError(
                    "No active PymoniK instance found. Please create one and pass it in or use the context manager."
                )
                
        merged_task_options = self._merge_task_options(pymonik, task_options, pmk_kwargs)
                
        # Handle the case of multiple tasks
        result_handles: List[ResultHandle[R_Type]] = self._invoke_multiple(args_list, pymonik, delegate, merged_task_options)
        return MultiResultHandle(result_handles)

    def __call__(self, *args, **kwds):
        return self.func(*args, **kwds)

    def _invoke_multiple(
        self, args_list: List[Tuple], pymonik_instance: "Pymonik", delegate: bool, task_options: TaskOptions, additional_kwargs: Optional[Dict[str, Any]] = None
    ) -> List[ResultHandle]:
        """Invoke a multiple tasks with the given arguments."""
        # Ensure we have an active connection and session

        if delegate and not pymonik_instance.is_worker():
            raise RuntimeError(
                "Delegation is only supported in worker mode. Please use the worker context."
            )

        if delegate and len(args_list) > 1:
            raise RuntimeError(
                "Delegation is only supported for a single task with a single result handle. Please use the invoke method, or combine the results into a single result."
            )

        if not pymonik_instance._connected:
            pymonik_instance.create()

        # Process arguments to extract ResultHandles for data dependencies
        if not pymonik_instance._session_created:
            raise RuntimeError(
                "No existing session to link the invocation to, create one first (hint: call create or use the context manager)"
            )

        #
        function_instance_remote_name = (
            pymonik_instance._session_id + "__function__" + self.func_name
        )

        if function_instance_remote_name not in pymonik_instance.remote_functions:
            pymonik_instance.register_tasks([self])

        function_id = pymonik_instance.remote_functions[
            pymonik_instance._session_id + "__function__" + self.func_name
        ].result_id

        all_function_invocation_info = []
        all_result_names = []
        all_payloads = {}
        for args in args_list:
            payload_name = f"{pymonik_instance._session_id}__payload__{self.func_name}__{uuid.uuid4()}"
            result_name = f"{pymonik_instance._session_id}__output__{self.func_name}__{uuid.uuid4()}"
            function_invocation_info = {
                "data_dependencies": [function_id],
                "payload_name": payload_name,
                "result_name": result_name,
            }
            processed_args = []
            # Prepare function call args description
            for arg in args:
                if arg is pymonik_instance.NoInput:
                    processed_args.append("__no_input__")
                elif isinstance(arg, ResultHandle):
                    function_invocation_info["data_dependencies"].append(arg.result_id)
                    processed_args.append(f"__result_handle__{arg.result_id}")
                elif isinstance(arg, MultiResultHandle):
                    # If it's a MultiResultHandle, add all result IDs as dependencies
                    for handle in arg.result_handles:
                        function_invocation_info["data_dependencies"].append(
                            handle.result_id
                        )
                    processed_args.append(
                        f"__multi_result_handle__"
                        + ",".join([handle.result_id for handle in arg.result_handles])
                    )
                elif isinstance(arg, Materialize):
                    if not arg.result_id:
                        raise ValueError(f"Materialize object must be uploaded first: {arg}")
                    # Add the materialized content as a dependency
                    function_invocation_info["data_dependencies"].append(arg.result_id)
                    # Pass the Materialize object directly (it will be pickled)
                    processed_args.append(arg)
                else:
                    processed_args.append(arg)

            # Serialize the function call information
            payload = pickle.dumps(
                {
                    "func_name": self.func_name,
                    "func_id": function_id,
                    "require_context": self.require_context,
                    "environment": pymonik_instance.environment,
                    "args": LazyArgs(processed_args),
                }
            )

            all_payloads[payload_name] = payload
            all_result_names.append(result_name)
            all_function_invocation_info.append(function_invocation_info)
        # Create result metadata for output

        if delegate:
            results_created = {
                all_function_invocation_info[0]["result_name"]: Result(
                    result_id=pymonik_instance.parent_task_result_id
                )
            }
        else:
            results_created = pymonik_instance._dispatch_create_metadata(
                all_result_names,
            )
        # Create the payloads for all the tasks to submit
        payload_results = pymonik_instance._dispatch_create_payloads(all_payloads)

        # Submit all the tasks:
        task_definitions = []
        for invocation_info in all_function_invocation_info:
            # Create the task definition
            # TODO: Wrap this for into a TaskInvocation object that can be manipulated for subtasking on the worker side of things
            task_definitions.append(
                TaskDefinition(
                    payload_id=payload_results[
                        invocation_info["payload_name"]
                    ].result_id,
                    expected_output_ids=[
                        results_created[invocation_info["result_name"]].result_id
                    ],
                    data_dependencies=invocation_info["data_dependencies"],
                )
            )

        # Submit the task
        pymonik_instance._dispatch_submit_tasks(
            task_definitions,  # TODO: use different batch size for tasks/results
            task_options
        )

        # Return a handle to the result
        result_handles = [
            ResultHandle(
                result.result_id, pymonik_instance._session_id, pymonik_instance
            )
            for result in results_created.values()
        ]
        return result_handles

class Pymonik:
    """A wrapper around ArmoniK for task-based distributed computing."""

    # A singleton to indicate that a task takes no input
    NoInput = object()

    def __init__(
        self,
        endpoint: Optional[str] = None,
        partition: Optional[Union[str, List[str]]] = "pymonik",
        environment: Dict[str, Any] = {},
        is_worker: bool = False,
        batch_size: int = 32,
        task_options: Optional[TaskOptions] = None,
        disable_events_client: bool = False,
        polling_interval: int = 1,
        polling_batch_size: int = 10,
        local_session: bool = False
    ):
        """Initializes a PymoniK client instance.

        This constructor sets up the configuration for interacting with an ArmoniK
        cluster. It can be configured to run as a client (submitting tasks)
        or on the worker (subtasking).

        Args:
            endpoint: The gRPC endpoint of the ArmoniK control plane
                (e.g., "localhost:5001"). If None, PymoniK might attempt
                to discover it from environment variables (e.g., AKCONFIG)
                during the `create()` call.
            partition: The ArmoniK partition ID where tasks will be
                submitted or processed. Defaults to "pymonik".
            environment: A dictionary specifying the execution environment
                for tasks. This can include configurations for dependencies,
                file mounts, or environment variables for the task runtime.
                Defaults to an empty dictionary.
            is_worker: If True, this instance operates in worker mode.
                Worker mode instances are typically managed by the ArmoniK agent
                and receive tasks to execute. They do not create sessions or
                submit new top-level tasks themselves but can submit sub-tasks.
                Defaults to False (client mode).
            batch_size: Default batch size for certain ArmoniK operations,
                such as creating multiple results or submitting tasks in bulk.
                Defaults to 32.
            task_options: Default `TaskOptions` to be used for tasks submitted
                by this client. These options include settings like maximum
                duration, priority, and retry attempts for tasks. If None,
                a default set of `TaskOptions` will be generated.
            disable_events_client: A flag to disable the use of the events client. This switches 
                to a polling based approach for waiting for results.
            polling_interval: When using the polling based approach, polling interval in seconds.
            polling_batch_size: Batch size to use when polling for results.
            local_session: A flag intended to control session behavior,
                for local testing, it makes it so your function invokes execute locally.
                Note: This parameter is not actively used in the current
                `__init__` body's logic but is stored for potential future use.
                Defaults to False.
        """
        self._endpoint = endpoint
        self._partition = partition
        self.task_options = task_options if task_options is not None else TaskOptions(
            max_duration=timedelta(seconds=300),
            priority=1,
            max_retries=5,
            partition_id=self._partition if isinstance(self._partition, str) else self._partition[0], # if using multiple partitions and no task options we just use the first partition specified,
        )
        self._connected = False
        self._session_created = False
        self.remote_functions = {}  # TODO: I should probably delete all these results when a session is closed.
        self.environment = environment
        self._token: Optional[contextvars.Token] = None
        self._is_worker_mode = is_worker
        self.disable_events_client = disable_events_client
        self.polling_interval = polling_interval
        self.polling_batch_size = polling_batch_size
        self.batch_size = batch_size
        self.task_handler: Optional[TaskHandler] = None
        self._original_sigint_handler = None
        self._sigint_handler_set = False

    def _handle_ctrl_c(self, signum, frame):
        """Custom SIGINT handler to cancel the session."""
        print(f"\nCtrl+C detected! Cancelling PymoniK session {self._session_id}...", file=sys.stderr)
        # It's important that cancel() is somewhat idempotent or handles being called multiple times
        self.cancel()

        # Restore the original handler before raising KeyboardInterrupt
        # This is important if the program has its own KeyboardInterrupt handling
        # or to ensure default behavior if this handler is somehow invoked again.
        if self._original_sigint_handler is not None:
            try:
                signal.signal(signal.SIGINT, self._original_sigint_handler)
            except (ValueError, OSError): # pragma: no cover (e.g. if not in main thread)
                 pass # Ignore if we can't restore (e.g., not in main thread)
            self._original_sigint_handler = None # Clear it after restoring
        
        self._sigint_handler_set = False # Mark that our handler is no longer active

        # Re-raise KeyboardInterrupt to ensure the script terminates as expected
        # or allows for further user-defined KeyboardInterrupt handling.
        raise KeyboardInterrupt

    def _dispatch_create_metadata(self, names: List[str]) -> Dict[str, Result]:
        """Internal method to create result metadata, dispatching to worker/client."""
        if self.is_worker():
            if not self.task_handler:
                raise RuntimeError("Task handler not available in worker mode.")
            # TaskHandler uses batch_size internally in the method call
            return self.task_handler.create_results_metadata(
                names, batch_size=self.batch_size
            )
        else:
            if not self._results_client:
                raise RuntimeError("Results client not initialized.")
            # ArmoniKResults client takes session_id and batch_size explicitly
            return self._results_client.create_results_metadata(
                names, self._session_id, batch_size=self.batch_size
            )

    def _dispatch_upload_payload(self, name: str, payload: bytes | bytearray) -> Dict[str, Result]:
        """Internal method to create upload data, dispatching to worker/client."""
        if self.is_worker():
            if not self.task_handler:
                raise RuntimeError("Task handler not available in worker mode.")
            # TaskHandler uses batch_size internally in the method call
            raise NotImplementedError(
                "TaskHandler does not support upload payloads."
            )
        else:
            if not self._results_client:
                raise RuntimeError("Results client not initialized.")
            # ArmoniKResults client takes session_id and batch_size explicitly
            return self._results_client.upload_result_data(
                name, self._session_id, result_data=payload
            )


    def _dispatch_create_payloads(
        self, payloads: Dict[str, bytes]
    ) -> Dict[str, Result]:
        """Internal method to create results with data (payloads), dispatching."""
        if self.is_worker():
            if not self.task_handler:
                raise RuntimeError("Task handler not available in worker mode.")
            return self.task_handler.create_results(
                payloads, batch_size=self.batch_size
            )
        else:
            if not self._results_client:
                raise RuntimeError("Results client not initialized.")
            return self._results_client.create_results(
                payloads, self._session_id, batch_size=self.batch_size
            )

    def _dispatch_submit_tasks(self, task_definitions: List[TaskDefinition], task_options: Optional[TaskOptions] = None) -> None:
        """Internal method to submit tasks, dispatching to worker/client."""
        if self.is_worker():
            if not self.task_handler:
                raise RuntimeError("Task handler not available in worker mode.")
            self.task_handler.submit_tasks(
                task_definitions,
                batch_size=self.batch_size,  # NOTE: this is bad, really bad (set client side but we just use the default for worker)
                default_task_options=task_options
            )
        else:
            if not self._tasks_client:
                raise RuntimeError("Tasks client not initialized.")
            self._tasks_client.submit_tasks(self._session_id, task_definitions, default_task_options=task_options)


    def _wait_for_results_availability(self, session_id: str, result_ids: List[str]):
        if self.disable_events_client:
            if not result_ids:
                return

            for batch_of_ids in batched(result_ids, self.polling_batch_size):
                if not batch_of_ids: # This should not happen (please)
                    continue
                
                _poll_batch_for_results(
                    results_client=self._results_client,
                    result_ids_in_batch=list(batch_of_ids), 
                    polling_interval_seconds=self.polling_interval
                )
        else:
            if self._events_client is None:
                raise RuntimeError(
                    "Events client (self._events_client) is not initialized. "
                    "Ensure Pymonik.create() has been called or is active in the current context."
                )
            return self._events_client.wait_for_result_availability(
                result_ids=result_ids,
                session_id=session_id,
                bucket_size=self.batch_size, # Use Pymonik's configured batch_size
                parallelism=1               # Sensible default for events client path here
            )

    def register_tasks(self, tasks: List[Task]):
        """Register a task with the PymoniK instance."""
        pickled_functions = {}
        for task in tasks:
            remote_function_name = self._session_id + "__function__" + task.func_name
            if remote_function_name in self.remote_functions:
                # This shouldn't be a full failure, but a warning, esp. in the case where the user is trying to register stuff manually (TODO: when logging is in)
                raise ValueError(
                    f"Task with name {task.func_name} is already registered. "
                )

            pickled_functions[remote_function_name] = pickle.dumps(task.func)
        # Upload the pickled functions to the cluster
        # NOTE: This is really bad for subtasking, other option would be to get results before invoke to check if task is already registered in this session and if so reuse it
        upload_results = self._dispatch_create_payloads(
            payloads=pickled_functions,
        )

        # Register the function
        self.remote_functions.update(upload_results)

        return self

    def _zip_directory(self, dir_path: str) -> bytes:
        """Zips the contents of a directory and returns the bytes."""
        if not os.path.isdir(dir_path):
            raise ValueError(f"Path {dir_path} is not a valid directory.")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create arcname relative to the directory being zipped
                    arcname = os.path.relpath(file_path, dir_path)
                    zipf.write(file_path, arcname)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    # TODO: put the task_handler and expected_output inside kwargs since they're only used internally inside the task context.
    # TODO: support TaskOptions as a parameter for PymoniK
    def create(
        self,
        task_handler: Optional[TaskHandler] = None,
        expected_output: Optional[str] = None,
    ) -> "Pymonik":
        """Initialize client connections and create a session.

        Args:
            task_handler (Optional[TaskHandler]): The task handler to use in worker mode.
        Returns:
            Pymonik: The current instance of Pymonik.
        """
        if self._is_worker_mode:
            if task_handler is None:
                raise ValueError("TaskHandler must be provided in worker mode.")
            self.task_handler = task_handler
            self._connected = True  # Mark as 'connected' in worker context
            self._session_id = task_handler.session_id  # Get session from handler
            self._session_created = True  # Mark session as 'created' in worker context
            self.parent_task_result_id = expected_output  # Store the expected output ID for the parent task to be used for subtasking.
            return self

        if self._connected:
            return self

        # TODO: Cloudpickle goes in here (maintain registrar of serialized functions, send them over during init, can also do dank thing here like with unison)

        # Initialize clients
        if self._endpoint != None:
            # TODO: Add parameters for TLS
            self._channel = create_grpc_channel(self._endpoint)
        else:
            # Check if AKCONFIG is defined
            akconfig_value = os.getenv("AKCONFIG")
            if akconfig_value is None:
                raise RuntimeError(
                    "No endpoint provided and AKCONFIG environment variable is not set."
                )
            else:
                # Load the AKCONFIG file
                with open(akconfig_value, "r") as f:
                    config = yaml.safe_load(f)
                self._endpoint = config.get("endpoint")
                certificate_authority = config.get("certificate_authority")
                client_certificate = config.get("client_certificate")
                client_key = config.get("client_key")
                self._channel = create_grpc_channel(
                    self._endpoint,
                    certificate_authority=certificate_authority,
                    client_certificate=client_certificate,
                    client_key=client_key,
                )

        self._tasks_client = ArmoniKTasks(self._channel)
        self._results_client = ArmoniKResults(self._channel)
        self._sessions_client = ArmoniKSessions(self._channel)
        self._events_client = ArmoniKEvents(self._channel)
        self._connected = True

        # Create a session
        self._session_id = self._sessions_client.create_session(
            default_task_options=self.task_options,
            partition_ids=[self._partition] if isinstance(self._partition, str) else self._partition,
        )
        self._session_created = True
        print(f"Session {self._session_id} has been created")

        # Upload environment data if needed
        # TODO: doesn't work as of right now
        # if self.environment and "mount" in self.environment:
        #     mounts_to_upload = {}
        #     mount_name_to_target_map = {}  # Maps temporary result name to mount_to path

        #     original_mounts = self.environment.get("mount", [])
        #     if not isinstance(original_mounts, list):
        #         print(
        #             f"Warning: 'mount' in environment should be a list of tuples. Skipping mount processing."
        #         )  # Or raise error
        #         original_mounts = []  # Clear it to avoid later errors

        #     for mount_info in original_mounts:
        #         if not isinstance(mount_info, tuple) or len(mount_info) != 2:
        #             print(
        #                 f"Warning: Invalid mount entry {mount_info}. Expected (mount_from, mount_to). Skipping."
        #             )
        #             continue

        #         mount_from, mount_to = mount_info
        #         print(
        #             f"Processing mount: Zipping {mount_from} for target {mount_to}..."
        #         )
        #         try:
        #             zip_bytes = self._zip_directory(mount_from)
        #             # Create a unique name for the result payload for this mount
        #             cleaned_mount_from = mount_from.replace("/", "_").replace("\\", "_")
        #             mount_result_name = (
        #                 f"{self._session_id}__mount_data__{cleaned_mount_from}"
        #             )
        #             mounts_to_upload[mount_result_name] = zip_bytes
        #             mount_name_to_target_map[mount_result_name] = mount_to
        #             print(
        #                 f"  ... Zipped {mount_from} ({len(zip_bytes)} bytes) -> {mount_result_name}"
        #             )
        #         except Exception as e:
        #             print(
        #                 f"  ... Error zipping directory {mount_from}: {e}. Skipping this mount."
        #             )
        #             # Decide if this should be a fatal error or just skip
        #             # raise # Uncomment to make it fatal

        #     if mounts_to_upload:
        #         print(f"Uploading {len(mounts_to_upload)} zipped directories...")
        #         # Upload the zipped directories as results
        #         upload_results = self._results_client.create_results(
        #             results_data=mounts_to_upload,
        #             session_id=self._session_id,
        #         )
        #         print("  ... Upload complete.")

        #         # Update self.environment["mount"] to store (result_id, mount_to) pairs
        #         updated_mount_info = []
        #         for mount_result_name, output in upload_results.items():
        #             if mount_result_name in mount_name_to_target_map:
        #                 mount_to = mount_name_to_target_map[mount_result_name]
        #                 result_id = output.result_id
        #                 updated_mount_info.append((result_id, mount_to))
        #                 print(
        #                     f"  ... Mapped {mount_result_name} (Result ID: {result_id}) to target path {mount_to}"
        #                 )
        #             else:
        #                 # This case should ideally not happen if logic is correct
        #                 print(
        #                     f"Warning: Uploaded result {mount_result_name} not found in mapping. Inconsistency detected."
        #                 )

        #         self.environment["mount"] = updated_mount_info
        #     else:
        #         # If nothing was successfully zipped and prepared for upload
        #         self.environment[
        #             "mount"
        #         ] = []  # Ensure it's an empty list if mounts were requested but failed


        return self

    def _ensure_client_ready(self):
        if self.is_worker():
            raise RuntimeError("Client operation attempted in worker mode.")
        if not self._connected or not self._session_created:
            self.create()
        if not self._results_client:
             raise RuntimeError("Results client not initialized after create().")
        if not self._session_id:
             raise RuntimeError("Session ID not available after create().")

    def upload_materialize(self, mat: Materialize, force_upload: bool = False) -> Materialize:
        """
        Upload a Materialize object to ArmoniK if it doesn't already exist.
        
        Args:
            mat: Materialize object to upload
            
        Returns:
            Materialize: Updated materialize object with result_id set
        """
        self._ensure_client_ready()
        
        # Check if result with this hash already exists
        hash_result_name = f"materialize_{mat.content_hash}"
        
        try:
            # Try to list results to see if one with this name exists
            # This is a simplified approach but it should work right?
            # ... surely..?
            
            # Query for existing results with our hash name
            existing_results = self._results_client.get_results_ids(
                session_id=self._session_id,
                names=[hash_result_name]
            )
            print(f"Existing Results = {existing_results}")
            if not force_upload and hash_result_name in existing_results:
                existing_result_id = existing_results[hash_result_name]
                print(f"Materialize content with hash {mat.content_hash} already exists: {existing_result_id}")
                mat.result_id = existing_result_id
                return mat
                
        except Exception as e:
            # If query fails, proceed with upload
            print(f"Could not check for existing materialize content: {e}")
        
        # Prepare content for upload
        if mat.is_directory:
            content_bytes = _create_zip_from_directory(mat.source_path)
        else:
            with open(mat.source_path, 'rb') as f:
                content_bytes = f.read()
        # Upload to ArmoniK
        upload_results = self._dispatch_create_payloads({hash_result_name: content_bytes})
        mat.result_id = upload_results[hash_result_name].result_id
        
        print(f"Uploaded materialize content: {mat.source_path} -> {mat.result_id} (hash: {mat.content_hash})")
        return mat

    def put(self, obj: U_Obj, name: Optional[str] = None) -> ResultHandle[U_Obj]:
        """
        Uploads a single Python object to ArmoniK.

        Args:
            obj: The Python object to upload.
            name: An optional name for this data. Used for traceability.

        Returns:
            A ResultHandle for the uploaded object.
        """
        self._ensure_client_ready() # Ensures create() is called if needed for client mode

        payload_bytes = pickle.dumps(obj)
        
        descriptive_name_part = name if name else str(uuid.uuid4())
        # This is the key used in the dictionary for _dispatch_create_payloads
        internal_payload_key = f"pymonik_put_data__{descriptive_name_part}"

        payloads_to_upload = {internal_payload_key: payload_bytes}
        
        # _dispatch_create_payloads returns a Dict[str, Result]
        # The keys in the returned dict match the keys in payloads_to_upload
        created_armonik_results_map = self._dispatch_create_payloads(payloads_to_upload)
        
        armonik_result_obj = created_armonik_results_map[internal_payload_key]

        return ResultHandle[U_Obj](
            result_id=armonik_result_obj.result_id, 
            session_id=self._session_id, # type: ignore (self._session_id is confirmed by _ensure_client_ready)
            pymonik_instance=self
        )

    def put_many(self, objects: List[V_Obj], names: Optional[List[str]] = None) -> List[ResultHandle[V_Obj]]:
        """
        Uploads multiple Python objects to ArmoniK.

        Args:
            objects: A list of Python objects to upload.
            names: An optional list of names for these objects. If provided,
                   its length must match the length of objects.

        Returns:
            A list of ResultHandles for the uploaded objects, in the same order.
        """
        self._ensure_client_ready()

        if not objects:
            return []

        if names and len(objects) != len(names):
            raise ValueError("Length of objects and names must match if names are provided.")

        payloads_to_upload: Dict[str, bytes] = {}
        ordered_internal_keys: List[str] = [] 

        for i, obj in enumerate(objects):
            payload_bytes = pickle.dumps(obj)
            
            descriptive_name_part = names[i] if names else str(uuid.uuid4())
            internal_payload_key = f"pymonik_put_many_data__{i}__{descriptive_name_part}" # Add index for more uniqueness
            
            payloads_to_upload[internal_payload_key] = payload_bytes
            ordered_internal_keys.append(internal_payload_key)
        
        created_armonik_results_map = self._dispatch_create_payloads(payloads_to_upload)
        
        result_handles = []
        for key in ordered_internal_keys:
            armonik_result_obj = created_armonik_results_map[key]
            result_handles.append(
                ResultHandle[V_Obj](
                    result_id=armonik_result_obj.result_id,
                    session_id=self._session_id, # type: ignore
                    pymonik_instance=self
                )
            )
        
        return result_handles

    def is_worker(self) -> bool:
        """Returns True if running in worker mode, False if in client mode."""
        return self._is_worker_mode

    def close(self):
        """Close the session and clean up resources."""
        if self._is_worker_mode:
            return

        if self._session_created:
            try:
                self._sessions_client.close_session(self._session_id)
                print(f"Session {self._session_id} has been closed")
                self._session_created = False
            except Exception as e:
                print(f"Error closing session {self._session_id}: {e}")

        if self._connected:
            self._channel.close()
            self._connected = False

    def cancel(self):
        """Cancel the session and clean up resources."""
        if self._is_worker_mode:
            return

        if self._session_created:
            try:
                self._sessions_client.cancel_session(self._session_id)
                print(f"Session {self._session_id} has been cancelled")
                self._session_created = False
            except Exception as e:
                print(f"Error cancelling session {self._session_id}: {e}")

        if self._connected:
            self._channel.close()
            self._connected = False

    def __enter__(self):
        """Context manager entry point."""
        # Workers have to create the session on their own
        if not self._is_worker_mode and not self._connected:
            self.create()
            # Set up the SIGINT (Ctrl+C) handler
            # This should only be done in the main thread.
            try:
                current_handler = signal.getsignal(signal.SIGINT)
                # Only set our handler if it's the default one or not already our instance's handler
                # This check helps prevent issues if __enter__ is called multiple times on the same instance
                # without __exit__ (though that would be unusual for a context manager).
                if current_handler is signal.default_int_handler or \
                   (not hasattr(current_handler, '__self__') or current_handler.__self__ is not self):
                    self._original_sigint_handler = signal.signal(signal.SIGINT, self._handle_ctrl_c)
                    self._sigint_handler_set = True
                # If current_handler is already self._handle_ctrl_c, _original_sigint_handler
                # would point to the one set before this Pymonik instance's handler,
                # or signal.default_int_handler if this is the first custom handler.
                # This logic aims to correctly chain/restore if multiple Pymonik contexts were nested,
                # though typically only one is active via _CURRENT_PYMONIK.

            except (ValueError, OSError, AttributeError):  # pragma: no cover
                # ValueError: signal only works in main thread
                # OSError: can also be raised (e.g. "not in main thread")
                # AttributeError: if getsignal returns something unexpected
                self._original_sigint_handler = None # Indicate we couldn't set it
                self._sigint_handler_set = False
                print("Warning: Could not set SIGINT handler. Ctrl+C might not cancel the session gracefully.", file=sys.stderr)

        self._token = _CURRENT_PYMONIK.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if self._token:
            _CURRENT_PYMONIK.reset(self._token)
            self._token = None
        # Restore the original SIGINT handler if we set one
        if not self._is_worker_mode and self._sigint_handler_set:
            if self._original_sigint_handler is not None:
                try:
                    signal.signal(signal.SIGINT, self._original_sigint_handler)
                except (ValueError, OSError):  # pragma: no cover
                    # In case we are in a state where it cannot be reset (e.g. thread changed)
                    print("Warning: Could not restore original SIGINT handler.", file=sys.stderr)
            self._original_sigint_handler = None # Clear it
            self._sigint_handler_set = False
        self.close()
        return False

def task(
    _func: Optional[Callable[P_Args,R_Type]] = None,
    *,
    require_context: bool = False,
    function_name: Optional[str] = None,
    task_options: Optional[TaskOptions] = None,
    partition: Optional[str] = None,
    max_duration: Optional[Union[timedelta, int, float]] = None,
    priority: Optional[int] = None,
    max_retries: Optional[int] = None,
) -> Union[Callable, Task]:
    """Decorator to create a Task from a function.
    
    Args:
        _func: The function to wrap (used internally by decorator syntax)
        require_context: Whether the task requires a PymonikContext
        function_name: Custom name for the function
        task_options: Complete TaskOptions object to use as defaults
        partition: Shortcut to specify partition_id
        max_duration: Maximum duration for the task (timedelta, or seconds as int/float)
        priority: Task priority 
        max_retries: Maximum number of retries
    
    Usage:
        @task
        def my_func():
            pass
            
        @task(partition="gpu", max_duration=600, priority=2)
        def gpu_func():
            pass
            
        @task(task_options=TaskOptions(max_duration=timedelta(minutes=10)))
        def complex_func():
            pass
    """
    def decorator(func: Callable[P_Args,R_Type]) -> Task[P_Args,R_Type]:
        resolved_name = function_name or func.__name__
        
        # Build task options from individual parameters
        decorator_task_options = None
        if (task_options is not None or 
            partition is not None or 
            max_duration is not None or 
            priority is not None or 
            max_retries is not None):
            
            # Start with provided task_options or create new one
            if task_options is not None:
                # Copy the existing task options
                base_max_duration = task_options.max_duration
                base_priority = task_options.priority
                base_max_retries = task_options.max_retries
                base_partition_id = task_options.partition_id
            else:
                # Use None as default, will be filled by Pymonik defaults later
                base_max_duration = None
                base_priority = None
                base_max_retries = None
                base_partition_id = None
            
            # Override with individual parameters
            final_max_duration = base_max_duration
            if max_duration is not None:
                if isinstance(max_duration, (int, float)):
                    final_max_duration = timedelta(seconds=max_duration)
                elif isinstance(max_duration, timedelta):
                    final_max_duration = max_duration
                    
            final_priority = priority if priority is not None else base_priority
            final_max_retries = max_retries if max_retries is not None else base_max_retries
            final_partition_id = partition if partition is not None else base_partition_id
            
            decorator_task_options = TaskOptions(
                max_duration=final_max_duration,
                priority=final_priority,
                max_retries=final_max_retries,
                partition_id=final_partition_id,
            )

        # # TODO: Remove        
        # print(f"Decorator Task Options {decorator_task_options}")
        
        return Task[P_Args,R_Type](
            func, 
            require_context=require_context, 
            func_name=resolved_name,
            task_options=decorator_task_options
        )

    if _func is None:
        # Case 1: Called with arguments - @task(...)
        return decorator
    else:
        # Case 2: Called without arguments - @task
        return decorator(_func)
