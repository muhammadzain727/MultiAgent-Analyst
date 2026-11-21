from agents.requirement_agent import requirement_agent
from agents.query_agent import query_agent
from agents.analyst_agent import analyst_agent

def main():

    question = input("What would you like to analyze? ")

    requirements = requirement_agent(question)

    # Retrieve data using query agent

    # Analyze data using analyst agent

    # Display final report


if __name__ == "__main__":
    main()