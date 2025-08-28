from vinagent.agent.agent import Agent
from vinagent.memory import Memory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import logging

load_dotenv()


llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
)


# Step 1: Create Agent with tools
agent = Agent(
    description="""You are an Advanced Academic Paper Research Assistant specialized in arXiv paper discovery and analysis.

Your primary responsibilities include:
- Conducting targeted searches on arXiv database using relevant keywords and topics
- Retrieving and organizing comprehensive paper metadata (titles, authors, abstracts, publication dates)
- Providing detailed information about specific papers using their arXiv IDs
- Helping users discover relevant research papers in their field of interest
- Offering insights and summaries based on paper abstracts and metadata

Guidelines for interaction:
- Always ask clarifying questions if the research topic is too broad or vague
- Suggest related keywords or topics when initial searches yield limited results
- Provide paper recommendations based on relevance and publication recency
- Format responses clearly with paper titles, authors, and key insights
- Use paper IDs consistently for reference and follow-up queries""",
    llm=llm,
    skills=[
        "Search arXiv database for academic papers using specific topics, keywords, or research areas",
        "Extract detailed metadata including titles, authors, abstracts, and publication information",
        "Retrieve comprehensive information about papers using their arXiv identification numbers",
        "Organize and present paper information in a structured, readable format",
        "Recommend relevant papers based on user research interests and current trends",
        "Assist with literature review preparation by finding papers in specific domains",
        "Cross-reference papers and identify research connections across different topics",
    ],
    tools=[
        "project.paper_research.tools.search_papers",
        "project.paper_research.tools.extract_paper_info",
    ],
    memory_path="templates/memory.json",
    is_reset_memory=True,
)


# Step 2: Create chat loop
def chat_loop():
    print("🔬 Academic Paper Research Assistant is ready!")
    print("I can help you search for papers on arXiv and extract detailed information.")
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("-" * 70)

    while True:
        try:
            # Get user input
            user_input = input("\n📝 You: ").strip()

            # Check for exit conditions
            if user_input.lower() in ["quit", "exit", "bye", "q"]:
                print("👋 Goodbye! Happy researching!")
                break

            # Skip empty inputs
            if not user_input:
                print("Please enter a message or 'quit' to exit.")
                continue

            # Invoke the agent
            response = agent.invoke(user_input, user_id="Lam", is_save_memory=True)
            print(f"🤖 Assistant: {response.content}")

        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")


if __name__ == "__main__":
    chat_loop()
