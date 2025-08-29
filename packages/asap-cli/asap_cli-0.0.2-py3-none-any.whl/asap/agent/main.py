import typer
# from utils.agents.factory_agent import AgentFactory
# from utils.agents.tools.general.llamagers import BedrockLLamager


# ANSI color codes
RESET = '\033[0m'
BOLD = '\033[1m'
GRAY = '\033[90m'
ORANGE = '\033[38;5;208m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
WHITE = '\033[97m'
CYAN = '\033[96m'


def print_welcome():
    
    
    
    # AWS Logo
    logo = [
        "█████╗ ██╗    ██╗███████╗",
        "██╔══██╗██║    ██║██╔════╝", 
        "███████║██║ █╗ ██║███████╗",
        "██╔══██║██║███╗██║╚════██║",
        "██║  ██║╚███╔███╔╝███████║",
        "╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝"
    ]
    
    print("\n")
    
    # Print AWS logo in gray
    for line in logo:
        print(f"{GRAY}{line.center(80)}{RESET}")
    
    # Print AWS logo in orange  
    for line in logo:
        print(f"{ORANGE}{line.center(80)}{RESET}")
    
    print("\n")
    
    # Header box
    print(f"{ORANGE}┌──────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{ORANGE}│{RESET} {ORANGE}{BOLD}ProServ Data & Analytics Latam Team{RESET}                              {ORANGE}│{RESET}")
    print(f"{ORANGE}│{RESET}                                                                      {ORANGE}│{RESET}")
    print(f"{ORANGE}│{RESET} You are connected to a Senior Data Engineer,                       {ORANGE}│{RESET}")
    print(f"{ORANGE}│{RESET} backed by the full expertise of {ORANGE}AWS{RESET} ProServ.                      {ORANGE}│{RESET}")
    print(f"{ORANGE}│{RESET}                                                                      {ORANGE}│{RESET}")
    print(f"{ORANGE}│{RESET} Let's accelerate your data migration journey.                       {ORANGE}│{RESET}")
    print(f"{ORANGE}└──────────────────────────────────────────────────────────────────────┘{RESET}")
    print()
    
    # Instructions
    print(f"{YELLOW}┌──────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{YELLOW}│{RESET}                           {YELLOW}{BOLD}INSTRUCTIONS{RESET}                           {YELLOW}│{RESET}")
    print(f"{YELLOW}│{RESET}                                                                      {YELLOW}│{RESET}")
    print(f"{YELLOW}│{RESET} {BLUE}①{RESET}Provide the SQL or ETL pipeline you want to migrate or translate {YELLOW}│{RESET}")
    print(f"{YELLOW}│{RESET} {BLUE}②{RESET}Always specify the exact pipeline name for better context        {YELLOW}│{RESET}")
    print(f"{YELLOW}│{RESET} {BLUE}③{RESET}The assistant will ask clarifying questions if needed             {YELLOW}│{RESET}")
    print(f"{YELLOW}│{RESET} {BLUE}④{RESET}Type 'exit' or 'quit' to end the session                         {YELLOW}│{RESET}")
    print(f"{YELLOW}└──────────────────────────────────────────────────────────────────────┘{RESET}")
    print()
    
    # Capabilities
    print(f"{WHITE}┌──────────────────────────────────────────────────────────────────────┐{RESET}")
    print(f"{WHITE}│{RESET}                            {WHITE}{BOLD}CAPABILITIES{RESET}                          {WHITE}│{RESET}")
    print(f"{WHITE}│{RESET}                                                                      {WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} 🔄 SQL/ETL Migration Between Platforms      (Oracle, Teradata → {ORANGE}AWS{RESET}){WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} ⚡ Query & Transformation Optimization      (Performance & Cost)    {WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} 🎯 Expert Migration Assessment               (Complexity & Risk Analysis){WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} 📋 Detailed Implementation Roadmaps         (Step-by-step Migration Plans){WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} 🏗️ {ORANGE}AWS{RESET}-Native Architecture Suggestions     (Glue, EMR, Redshift, Athena){WHITE}│{RESET}")
    print(f"{WHITE}│{RESET} 🛡️ Data Quality & Validation Strategies     (Testing & Validation)     {WHITE}│{RESET}")
    print(f"{WHITE}└──────────────────────────────────────────────────────────────────────┘{RESET}")
    print()

def run_agent(translate_agent):
    print_welcome()

    while True:
        try:
            query = input(f"{CYAN}aws-proserv:~$ {RESET}").strip()
            if query.lower() in {"exit", "quit"}:
                print(f"{ORANGE}Thanks for using AWS ProServ Migration Assistant!{RESET}")
                break

            # 🚀 Call sync run (no await needed)
            translate_agent.run(query, "1")

        except KeyboardInterrupt:
            print(f"\n{ORANGE}Session terminated. Goodbye!{RESET}")
            break
        except EOFError:
            print(f"\n{ORANGE}Session ended.{RESET}")
            break

def register(app: typer.Typer):
    agent_app = typer.Typer(help="⚡ Start the agent with command [run]")
    app.add_typer(agent_app, name="agent")

    @agent_app.command("run")
    def run_agent_command():
        """
        Execute the agent with its configured tools.
        """

        from asap.agent.utils.agents.factory_agent import AgentFactory
        from asap.agent.utils.agents.tools.general.llamagers import BedrockLLamager

        translate_agent = AgentFactory()
        BedrockLLamager.new_instance("reasoning", model="us.anthropic.claude-sonnet-4-20250514-v1:0")
        run_agent(translate_agent)

