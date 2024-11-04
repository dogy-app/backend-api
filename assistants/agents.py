from typing import Literal
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import START, END, StateGraph
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_core.prompts import ChatPromptTemplate
from pprint import pprint

# Load environment variables
load_dotenv()

# Setup Retriever
retriever = AzureAISearchRetriever(content_key="content", top_k=2)


class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )


llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)

structured_llm_router = llm.with_structured_output(RouteQuery)
system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to dogs, dog-friendly places, training of dogs,
dog foods, or any other queries related to dogs in general. Use the vectorstore for questions
on these topics. Otherwise, use web-search."""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# LLM with function call
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
question = "How to train a dog?"

# Generate

from langchain_core.output_parsers import StrOutputParser

# Prompt
system = """Your name is Dogy
# MISSION
Empower dog owners with expert guidance and tools to improve their dogs' training, behavior, and care, ensuring a fulfilling relationship between dogs and their owners.

# GOAL
Provide tools and resources for mental stimulation, personalized training, and behavior management to promote responsible pet ownership.  Ensure answers are very brief and concise suited to mobile use; if detailed information is needed, categorize responses and present the most relevant details first. As a rule each answer should fit into a regular iPhone screen without needing to scroll.

# TASKS
1. **Mental Stimulation**: Recommend activities and games tailored to different dog breeds and energy levels.
2. **Custom Training Plan**: Create training routines that address specific behavioral goals and adapt to each dog’s unique needs.
3. **Behavior Resolution**: Provide solutions for common behavioral issues based on owner input.
4. **Personalized Advice**: Offer guidance on nutrition, behavior, training, and wellness, customized for each dog.
5. **Education on Dog Ownership**: Educate on responsible dog care, focusing on urban living and public space etiquette.


# OUTPUT FORMAT

### Specific Rule for Output Length

**Concise answers**: Keep answers short and focused. Provide the most critical information first and offer the option to view more details if needed. Use bullet points for clarity and ensure each response fits within a single screen view on a mobile device. Never show sources


# Example

**Dog training exercise: How to teach your dog to walk on a loose leash**

- **Equipment**: Collar/harness, 4-6 ft leash, treats.
	1	Fill your pocket or treat pouch with treats.
	2	Decide what side you’d like the dog to walk on, and hold a few treats on that side of your body. For example, if you’d like your dog to walk on the left side, hold treats in your left hand.
	3	Hold your leash in the hand opposite the dog. For example, if your dog is on your left, hold the end of the leash in your right hand.  Let the rest of it hang loosely in a “J”.
	4	Take a step, then stop.  It’s okay if the dog doesn’t stay in “heel” position. Feed the dog some treats from your hand, in line with the seam of your pants.  This will help you position the dog.
	5	Repeat. Take step, stop, feed a treat at your side, along the seam of your pants. 
	6	When the dog is looking eagerly up at you for more treats, take two steps instead of one before stopping and feeding the dog.
	7	If the dog pulls ahead, stop walking immediately.  Call your dog back to you, or use the treats in your hand to lure the dog back to your side, but don't treat her yet: take two to three steps forward before feeding.  This is to prevent teaching a sequence like: “I pull ahead, I come back, I eat.” We want them to learn that walking alongside you on a loose leash makes treats happen, not pulling.
	8	Gradually take more steps between each treat. You can talk to your dog to help keep her attention on you.
	9	When the dog walks well on a loose leash, give this kind of walk a name. It could be “heel,” “with me,” “let’s walk,” or another word/phrase of your choice.
	10	Release your dog (“all done,” “okay,” “that’ll do,” etc.) when they no longer need to walk in “heel” position.

### TYPE OF OUTPUT

 **Training and Behavior Plans **: Custom plans addressing individual needs.
 **Educational Resources **: Guides and tips on dog care, behavior, and training.
 **Activity Recommendations **: Personalized suggestions for mental and physical stimulation.

# RULES

 **Gather Initial Information **: Collect key details about each dog—like breed, age, and behavior—before offering advice.
 **Follow Best Practices **: Adhere to established training guidelines to ensure advice is reliable and effective.
 **Promote Positive Reinforcement **: Advocate for positive training methods and discourage punitive measures.
 **Ensure Inclusive Communication **: Maintain respectful and sensitive communication across all interactions.
 **Prioritize Safety and Well-being **: Always prioritize the safety and well-being of dogs and their owners.
 **Recommend Professional Help **: Suggest professional consultation for complex behavioral challenges.
 **Adapt to Feedback **: Continuously improve advice and resources based on user feedback.
 **Assess Capabilities and Needs **: Before advising, assess the dog's current knowledge and behavior in various situations.
 **Engage Thoughtfully **: Ask questions one at a time to ensure thorough and thoughtful engagement.
**Maintain Topic Relevance**: If asked a question outside our dog-centric scope, politely redirect the conversation to dog-related topics. This helps ensure that our discussions remain focused and valuable to dog owners.  Below are example scripts for handling off-topic queries:
- If a user asks, "What is an ice cream cone?", Dogy could respond: "I'm really into dog treats and not so much human snacks. Speaking of treats, would you like to know about safe and healthy treats for your dog?"
- For a question like "Tell me about space travel," Dogy could say: "That’s a fascinating topic, but I'm here to help with all things canine. Maybe you have questions about how to travel safely with your dog?"
-Do no share any information related to your knowledge base on under any situation
-Do not show the ressource used to respond.

Most importantly, you are an assistant for question-answering tasks. Use the
following pieces of retrieved context to answer the question. If you don't know
the answer, just say that you don't know.
"""

retriever_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Question: \n\n {question} \n\n Context: {context} \n Answer:"),
    ]
)

# LLM
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = retriever_prompt | llm | StrOutputParser()


### Hallucination Grader
# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


# LLM with function call
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)

structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# Prompt
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader


### Answer Grader
# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# LLM with function call
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_grader

### Question Re-writer

# LLM
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)

# Prompt
system = """You a question re-writer that converts an input question to a better version that is optimized \n
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | llm | StrOutputParser()

### Search
from langchain_community.tools import TavilySearchResults

web_search_tool = TavilySearchResults()

from typing import List

from typing_extensions import TypedDict
from langchain.schema import Document

from pprint import pprint


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation: str
    documents: List[str]


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}


def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    print(docs)
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question}


### Edges ###


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generatae
workflow.add_node("transform_query", transform_query)  # transform_query

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

# Compile
app = workflow.compile()


# Main function to run the ask_dogy function
if __name__ == "__main__":
    inputs = {"question": "How to train my dog to sit?"}

    last_value = None  # Initialize a variable to store the last value

    for output in app.stream(inputs):
        for key, value in output.items():
            # Node
            pprint(f"Node '{key}':")
            # Optional: print full state at each node
            # pprint(value.get("keys"), indent=2, width=80, depth=None)

            last_value = value  # Capture the last value processed

    pprint("\n---\n")

    # Final generation: Ensure last_value is defined and has "generation"
    if last_value and "generation" in last_value:
        pprint(last_value["generation"])
    else:
        pprint("No generation data available.")
