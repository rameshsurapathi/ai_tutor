# ==================================================================================================
# File: ai_iit_teacher.py
#
# Description:
# This script implements a conversational AI agent that acts as an expert teacher for
# IIT JEE subjects (Maths, Physics, Chemistry). It uses the LangGraph library to create a
# stateful, multi-step workflow that mimics a teacher's thought process: analyzing a
# student's question, identifying the core topic, creating a simple explanation,
# adding a real-world analogy, and finally, composing a complete, encouraging response.
# The agent is designed to be modular and can be configured for different subjects.
# ==================================================================================================

# --- Import necessary libraries ---
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

import uuid

# Import the memory module to handle conversation history
from src.memory import get_memory_saver

# Import the prompts used in the agent's workflow
from src.prompts import analyze_question_prompt, identify_topic_prompt, create_explanation_prompt, add_analogy_prompt, finalize_response_prompt, system_prompt_template, classify_question_prompt

# Import subject-specific data for examples and sample questions
from src.subject_data import TOPIC_EXAMPLES, SAMPLE_QUESTIONS

# --- Load environment variables from a .env file ---
# This is used to securely load the API key.
load_dotenv()


# --- Define the structure of the agent's state ---
# AgentState is a TypedDict that defines the data structure passed between nodes in the graph.
# It holds all the information the agent needs to process a request, from the initial
# question to the final response.

class AgentState(TypedDict):
    messages: list[ SystemMessage | HumanMessage | AIMessage ] # A list to keep track of the conversation history.
    question : str # The student's original question.
    topic_identified: str # The topic and subtopic identified by the agent.
    explanation: str # The step-by-step explanation of the concept.
    analogy: str # The real-world analogy for the concept.
    final_response: str # The complete, formatted response for the student.
    question_type: str # The type of the question: 'casual' or 'subject'.

# --- Define the main class for the AI Teacher Agent ---
class IIT_Teacher():
    """
    A class representing the AI Teacher agent. It encapsulates the logic for
    processing a student's question through a predefined graph of operations.
    """

    # --- Add a simple in-memory cache for repeated questions ---
    _response_cache = {}

    def __init__(self,subject, api_key:str):
        """
        Initializes the IIT_Teacher agent.
        
        Args:
            subject (str): The subject the teacher will specialize in (e.g., 'maths', 'physics').
            api_key (str): The API key for the language model service.
        """
        # Initialize the language model (LLM) from Google GenAI.
        self.llm = init_chat_model("google_genai:gemini-2.5-flash", temperature=0.1)
        
        # Store the subject and create a dynamic system prompt based on it.
        self.subject = subject.lower()
        self.system_prompt = system_prompt_template.format(subject=self.subject.capitalize())

        # Build the computational graph that defines the agent's workflow.
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """
        Builds the LangGraph workflow for the agent.
        
        This method defines the nodes (steps) and edges (transitions) of the agent's
        thought process.
        
        Returns:
            A compiled LangGraph object.
        """
        workflow = StateGraph(AgentState)

        # --- Define the nodes in the graph ---
        # Each node is a function that performs a specific task.
        workflow.add_node("classify_question", self.classify_question)
        workflow.add_node("analyze_and_identify", self._analyze_and_identify)  # Combined node
        workflow.add_node("explain_with_analogy", self._explain_with_analogy)
        workflow.add_node("finalize_response", self._finalize_response)

        # --- Define the edges connecting the nodes ---
        # This creates a linear sequence of operations.
        workflow.add_edge(START, "classify_question") # The graph starts at the 'classify_question' node.
        
        # Define routing based on the question type classified by the LLM.
        def route_from_classify(state: AgentState):
            if state.get("question_type") == "casual":
                return END  # End the graph for casual messages
            else:
                return "analyze_and_identify"
        
        # Conditional edges based on the classification result.
        workflow.add_conditional_edges("classify_question", route_from_classify)

        # Edges for the regular subject analysis workflow.
        workflow.add_edge("analyze_and_identify", "explain_with_analogy")
        workflow.add_edge("explain_with_analogy", "finalize_response")
        workflow.add_edge("finalize_response", END) # The graph ends after the 'finalize_response' node.

        # Compile the graph into a runnable object.
        return workflow.compile()
    
    # --- Node 1: Classify the student's question ---
    def classify_question(self, state: AgentState) -> AgentState:
        """
        Uses the LLM to classify if the question is a casual/greeting or subject-related.
        If casual, the LLM also generates a friendly reply.
        """
        question = state['question']
        prompt = classify_question_prompt.format(question=question)
        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ])
        content = response.content.strip()
        if content.startswith("casual|"):
            state["question_type"] = "casual"
            state["final_response"] = content.split("|", 1)[1].strip()
            return state  # Immediately return for casual, skip further processing
        elif content.startswith("subject|"):
            state["question_type"] = "subject"
        else:
            # fallback: treat as subject
            state["question_type"] = "subject"
        return state

    # --- Node 2: Analyze question and identify topic together ---
    def _analyze_and_identify(self, state:AgentState)->AgentState:
        """
        Analyzes the student's question to understand their confusion and identifies the main topic and subtopic in a single LLM call.
        """
        question = state['question']
        subject = self.subject
        examples = TOPIC_EXAMPLES.get(subject, "")
        prompt = (
            f"As an IIT {subject} teacher, analyze this student's question and identify the main topic and subtopic.\n"
            f"Question: {question}\n\n"
            "1. What is the student really asking? What concept are they struggling with? Respond in one clear sentence.\n"
            "2. Identify the main topic and subtopic. Format: Topic: [Main Topic] | Subtopic: [Specific Concept]\n"
            f"{examples}"
        )
        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ])
        # Parse the response
        content = response.content
        lines = content.split("\n")
        analysis = ""
        topic = ""
        for line in lines:
            if line.strip().startswith("Topic:"):
                topic = line.strip()
            elif line.strip():
                analysis = line.strip()
        state["messages"] = [SystemMessage(content=self.system_prompt), HumanMessage(content=prompt), response]
        state["topic_identified"] = topic
        # Optionally store the analysis if you want to use it later
        state["analysis"] = analysis
        return state

    # --- Node 3 Combined: Create explanation and analogy together ---
    def _explain_with_analogy(self, state:AgentState)->AgentState:
        """
        Generates a step-by-step explanation and a real-world analogy in a single LLM call.
        """
        question = state['question']
        topic = state['topic_identified']
        prompt = (
            f"The student asked: '{question}'\n"
            f"Topic identified: {topic}\n\n"
            "Create a simple, step-by-step explanation that a beginner can understand, "
            "and then provide a memorable real-world analogy to clarify the concept.\n\n"
            "Format your response as:\n"
            "Explanation: <your explanation>\n"
            "Analogy: <your analogy>"
        )
        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ])
        # Parse the response
        content = response.content
        explanation = ""
        analogy = ""
        if "Explanation:" in content and "Analogy:" in content:
            parts = content.split("Analogy:")
            explanation = parts[0].replace("Explanation:", "").strip()
            analogy = parts[1].strip()
        else:
            explanation = content.strip()
        state["explanation"] = explanation
        state["analogy"] = analogy
        return state

    # --- Node 4: Finalize the response ---
    def _finalize_response(self,state:AgentState)->AgentState:
        """
        Combines all generated parts (explanation, analogy) into a single, cohesive response.
        """
        question = state['question']
        topic = state['topic_identified']
        explanation = state['explanation']
        analogy = state["analogy"]
        prompt = finalize_response_prompt.format(question=question, topic=topic, explanation=explanation, analogy=analogy)
        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ])
        state["final_response"] = response.content
        return state

    # This method serves as the entry point for the agent to process a student's question.
    # It initializes the state and invokes the graph to get the final response.
    def teach(self, question:str)->str:
        """
        The main entry point for the agent to answer a question.
        Now includes caching and optional memory usage.
        
        Args:
            question (str): The student's question.
            
        Returns:
            str: The final, formatted response from the agent.
        """
        # Check cache first
        cache_key = (self.subject, question.strip().lower())
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Define the initial state for the graph.
        inital_state = {
            "messages" : [],
            "question" : question,
            "topic_identified" : "",
            "explanation" : "",
            "analogy" : "",
            "final_response" : ""
        }

        # If you don't need persistent memory, you can comment out the next two lines:
        # memory = get_memory_saver()
        # session_id = str(uuid.uuid4())
        # config = {"configurable": {"thread_id": session_id},"checkpoint_manager": memory}
        # result = self.graph.invoke(inital_state, config=config)

        # Instead, just call the graph directly:
        result = self.graph.invoke(inital_state)

        final_response = result['final_response']
        # Store in cache
        self._response_cache[cache_key] = final_response
        return final_response


# --- Main execution block ---
def main():
    """
    Handles the main user interaction loop: setting up the agent,
    taking user input, and printing the agent's response.
    """
    # Retrieve the API key from environment variables.
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set the API KEY as a environment variable")
        return

    # --- Get Student and Subject Info ---
    student_name = input("👨‍🏫 Teacher: Hello! What's your name?\n📚 Student: ")
    subject_input = input(f"👨‍🏫 Teacher: Nice to meet you, {student_name}! Which subject would you like to learn today? (Maths, Physics, or Chemistry)\n📚 Student: ")
    subject = subject_input.lower()

    # --- Subject-based setup ---
    if subject not in ["maths", "mathematics", "physics", "chemistry"]:
        # Handle invalid subject input.
        #print("👨‍🏫 Teacher: Please enter a valid subject name, I can teach.")
        #return
        subject = "maths"
    
    # Based on the user's choice, instantiate the teacher and set up sample questions.
    
    sample_questions = SAMPLE_QUESTIONS.get(subject, [])

    # Create an instance of the IIT_Teacher with the selected subject and API key.
    print(f"\n👨‍🏫 Teacher: Great choice! I will be your IIT {subject.capitalize()} teacher.")
    teacher = IIT_Teacher(subject,api_key)

    # --- Start the conversation loop ---
    print(f"\n🎓 IIT {subject.capitalize()} Teacher AI is ready!")
    print(f"\n🎓 Ask any {subject} question and get simple explanations with analogies.\n")
    print(f"\n🎓 Sample Questions you can ask {sample_questions}")

    while(True):
        question = input("\n📚 Student: ")
        # Allow the user to exit the conversation.
        if question.lower() in ['quit', 'exit', 'bye','thanks','thank you']:
            print(f"👨‍🏫 Teacher: Happy learning! Keep exploring {subject}!")
            break  

        # Process the question if it's not empty.
        if question.strip():
            try:
                print("\n👨‍🏫 Teacher: Let me explain this step by step...\n")
                # Get the response from the teacher agent.
                response = teacher.teach(question)
                print(response)
            except Exception as e:
                # Handle any errors during the process.
                print(f"\n👨‍🏫 Sorry, I encountered an error: {e}")
                print("\n👨‍🏫 Please try asking your question again.")

# --- Script entry point ---
# This ensures that the main() function is called only when the script is executed directly.
if __name__=="__main__":
    main()