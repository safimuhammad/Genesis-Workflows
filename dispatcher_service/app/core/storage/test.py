from helpers import connection_handler
from database import SQLstore


store = SQLstore()
store.create_connection
# task table
store.create_table()
store.add_task("Test task 1")
# task plan table
store.create_task_plan_table()
task_plan = {
    "thoughts": "",
    "graph": "",
    "ability": "",
}
TASK_ID = "e63ae3f4-d6d6-4850-a8f5-790e50419919"
store.add_task_plan(TASK_ID, task_plan)

# store.delete_task("0f227ecd-8318-49d9-a5d2-3c11e3200daf")
# Memory store
store.create_agent_memory_table()
store.insert_agent_memory(
    "123",
    "timestamp12",
    "bob",
    "input",
    "content=None",
    "artifacts=None",
    "agent_name=None",
    "sub_task _id=None",
    " metadata=None",
)

# memory = {
#     # "session_id": store.get_session_id,
#     "task_id": TASK_ID,
#     "artifacts": "",
#     "type_": "input",
#     "agent_name": "write_agent",
#     "sub_task_id": 123,
# }
# store.insert_agent_memory(**memory)
# print(store.fetch_agent_memory(session_id="9788c7dd-b84b-43e5-98e4-6ba47d37c5fc"))
# store.delete_agent_memory(session_id="9788c7dd-b84b-43e5-98e4-6ba47d37c5fc")
