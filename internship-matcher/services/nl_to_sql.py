import os
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.agents import create_agent
from yarl import Query
from prompts import nl_to_sql_prompts as promptsBank
import requests, pathlib
from langchain_community.utilities import SQLDatabase

os.environ["HUGGINGFACEHUB_API_TOKEN"] = ""


llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    temperature=0.7,
    model_kwargs={
        "max_tokens": 1024
    }
)

model = ChatHuggingFace(llm=llm)



# url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
# local_path = pathlib.Path("Chinook.db")
# if local_path.exists():
#     print(f"{local_path} already exists, skipping download.")
# else:
#     response = requests.get(url)
#     if response.status_code == 200:
#         local_path.write_bytes(response.content)
#         print(f"File downloaded and saved as {local_path}")
#     else:
#         print(f"Failed to download the file. Status code: {response.status_code}")


DATABASE_URL = "postgresql://ai_readonly:strong_password@localhost:5433/jobsdb"


db = SQLDatabase.from_uri(DATABASE_URL)

print(f"Dialect: {db.dialect}")
print(f"Available tables: {db.get_usable_table_names()}")
# print(f'Sample output: {db.run("SELECT * FROM jobs LIMIT 5;")}')


from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()


for tool in tools:
    print(f"{tool.name}: {tool.description}\n")


system_prompt = promptsBank.getPromptV0(db.dialect)


agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
)

question = "Give me the titles of all jobs"

# for step in agent.stream(
#     {"messages": [{"role": "user", "content": question}]},
#     stream_mode="values",
# ):
#     step["messages"][-1].pretty_print()

final_output = agent.invoke(
    {"messages": [{"role": "user", "content": question}]}
)


query =final_output['messages'][-1].content

print(final_output)
print(query)
