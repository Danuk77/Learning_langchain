import os

from langgraph.graph.graph import Checkpointer

from langchain_snl.configuration import Configuration, get_configuration
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage, system
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.runnables.config import RunnableConfig

model = ChatBedrock(
    model_id="anthropic.claude-v2:1",
    model_kwargs=dict(temperature=0)
)

def example():
    #messages = [SystemMessage(content="Translate the following from English to Sinhalese"), HumanMessage(content="Hello")]
    parser = StrOutputParser()
    system_template = "Translate the following into {language}"
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    chain = prompt_template | model | parser
    result = chain.invoke({"language": "Sinhala", "text": "I am sitting on a chair right now"})
    print(result)


def chat_model():
    workflow = StateGraph(state_schema=MessagesState) 
    
    def call_model(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": response}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    memory = MemorySaver()
    app = workflow.compile(checkpointer = memory)

    config = {"configurable": {"thread_id": "abc123"}}
    query = "Hi! I'm Bob."

    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    #output["messages"][-1].pretty_print()  # output contains all messages in state

    config = {"configurable": {"thread_id": "abc1234"}}
    query = "What is my name?"
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()

def chat_model_with_prompt_template():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a very shy person. Answer all questions to the best of your ability"),
            MessagesPlaceholder(variable_name="messages")
        ]
    ) 

    workflow = StateGraph(state_schema=MessagesState)

    def call_model(state: MessagesState):
        chain = prompt | model
        response = chain.invoke(state)
        return {"messages": response}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": "abc345"}}
    query = "Hi! I'm Jim."

    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    output["messages"][-1].pretty_print()
