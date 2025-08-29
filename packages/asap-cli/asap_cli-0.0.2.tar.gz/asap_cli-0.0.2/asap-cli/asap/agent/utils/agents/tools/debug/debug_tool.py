from langchain_core.tools import tool
from asap.agent.utils.agents.tools.general.llamagers import BedrockLLamager
from asap.agent.utils.agents.tools.general.prompts import CORRECTION
from asap.agent.utils.agents.tools.general.tools_input_class import debugSQl
from asap.agent.utils.general.ui import with_animation
from pydantic import BaseModel, Field
import pandas as pd
import os 
import time

class CorrectionAnswer(BaseModel):
    resume_of_fixes: str = Field(description="""resume of comments related to the corrections, maintain concise
                                 Use bullet points.

                                Each bullet must strictly follow this format:
                                “I did X → this matters because Y”

                                Add emojis for clarity 🎯
                                 """)
    fixed_sql: str = Field(description="ready fixed query or code based on user requirements and expected result")



class DataDebug: 

    def __init__(self, pipeline: str, user_requirement: str, test_case_name: str):
        self.pipeline= pipeline
        self.user_requirement = user_requirement
        self.test_case_name = test_case_name
        BedrockLLamager.new_instance("fast", model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")
        

    def run(self):
        
        # 1. Get the expected result, actual result, and target sql (check) 
        # 2. prompt for correction. (check)
        # 3. Add feedback loop. (check)
        # 4. Save fixed SQL with comments. (check)
        # 5. Add corrections notes to the assesment. (pending)
        # 6. Create the agent tool. 
        
        expected_result_path = f"migration/{self.pipeline}/expected_result/{self.test_case_name}.csv"
        query_result_path = f"migration/{self.pipeline}/query_result/{self.test_case_name}.csv"
        target_sql = f"migration/{self.pipeline}/target_sql"
        
        data = {
            "target_sql": self.__read_single_file_from_path(target_sql),
            "query_result":  self.__read_csv_as_markdown(query_result_path),
            "expected_result": self.__read_csv_as_markdown(expected_result_path)
        }

        self.correction(data)

        target_directory = f"migration/{self.pipeline}/target_sql"
        

        self.__save_file(self.pipeline, ".sql", self.fixed_sql, directory=target_directory)
        
        return f"The user requirement {self.user_requirement} was achieved succesfully, {self.pipeline} debugging was succesfull"


    def correction(self, data: dict): 

        prompt = CORRECTION

        # #### temporal change this
        # user_requirements=""
        user_query = f"""
        
        {self.user_requirement}

        query or code for check:  

        {data["target_sql"]}

        expected_result: 

        {data["expected_result"]}

        actual_result: 

        {data["query_result"]}
        """

        messages = [
            (
                "system",
                prompt,
            ),
            ("human", user_query),
        ]

        
        print("=" * 60)
        print("🚀 Starting Correction Task")
        print("=" * 60)
        print("Im gonna start understanding the code and expected result, to make the necessary corections 🔥...\n")
        
            
        # ai_msg = self.__call_llm(messages)
        ai_msg = self.__call_llm(messages)
        #self.assesment = ai_msg.content
        
        
        # Pretty print before showing final response
        print("\n" + "=" * 60)
        print("✅ Correction Ready")
        print("=" * 60)
        time.sleep(0.5)
        print(f"Comments: \n\n {ai_msg.resume_of_fixes} \n\n")
        print(f"Query fixed: \n\n {ai_msg.fixed_sql} \n\n") 
        print("=" * 60)

        self.resume_of_fixes = ai_msg.resume_of_fixes
        self.fixed_sql = ai_msg.fixed_sql

        finish = True 
        while finish == True:
            finish, user_feedback = self.__feedback_loop()

            if user_feedback != "":

                messages = [
                        (
                            "ai",
                            f"comments: {ai_msg.resume_of_fixes} fixed_query: {ai_msg.fixed_sql}",
                        ),
                        ("human", user_feedback),
                    ]
                
                print("Feedback recieved ✅, Im going to applied this feedback")    
                ai_msg = self.__call_llm(messages)
                print("\n" + "=" * 60)
                print("✅ Feedback applied")
                print("=" * 60)
                time.sleep(0.5)
                print(f"Comments: \n\n {ai_msg.resume_of_fixes} \n\n")
                print(f"Query fixed: \n\n {ai_msg.fixed_sql} \n\n") 
                self.resume_of_fixes = ai_msg.resume_of_fixes
                self.fixed_sql = ai_msg.fixed_sql
                print("=" * 60)

    

        
    @staticmethod
    def __read_csv_as_markdown(file_path: str) -> str:
        """
        Reads a CSV file and returns its content as a Markdown table.

        Conditions:
        - If file does not exist → raise FileNotFoundError
        - If file extension is not .csv → raise ValueError
        """
        # Check existence
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check extension
        if not file_path.lower().endswith(".csv"):
            raise ValueError("Only .csv files are allowed")
        
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Convert to Markdown table
        return df.to_markdown(index=False)


    @staticmethod
    def __feedback_loop():
                
        feedback = input("\nWould you like to refine ? (y/n): ").strip().lower()
        if feedback != "y":
            print("✅ accepted. Process complete.")
            return False, ""
            

        user_feedback = input("\n✏️ Please enter your feedback: ").strip()
        if not user_feedback:
            print("⚠️ No feedback provided. Skipping refinement.")
            return False, "" 

        return True, user_feedback
    
    @staticmethod
    def __save_file(pipeline_name: str, extension: str, content: str, directory: str = "migration"):
            """
            Saves a file for a pipeline with the given name and extension.

            Parameters:
                pipeline_name (str): The name of the pipeline (used as filename).
                extension (str): File extension, must be either '.sql' or '.md'.
                content (str): Content to save inside the file.
                directory (str): Directory (can be nested) where the file will be saved (default: 'pipelines').

            Raises:
                ValueError: If the extension is not allowed.
            """
            allowed_extensions = {".sql", ".md"}
            if extension not in allowed_extensions:
                raise ValueError(f"Invalid extension '{extension}'. Allowed: {allowed_extensions}")

            # ✅ Create directory if it doesn't exist (including nested)
            os.makedirs(directory, exist_ok=True)

            # Build full file path
            filename = f"{pipeline_name}{extension}"
            filepath = os.path.join(directory, filename)

            # Write content to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return filepath
    
    
    
    @staticmethod
    @with_animation("Thinking...")
    def __call_llm(messages: str):
        
        
        instance = BedrockLLamager.instance("fast")
        model = instance.get_model()
        structured_llm = model.with_structured_output(CorrectionAnswer)
        response = structured_llm.invoke(messages)

        return response


    @staticmethod
    def __read_single_file_from_path(path):
        
        # Check if path is empty
        if not path:
            return "The path is empty. ERROR"
        
        # Check if the path exists and is a directory
        if not os.path.isdir(path):
            return f"The path '{path}' does not exist or is not a directory. ERROR"

        # List all files in the directory
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # Check if there are no files
        if not files:
            return "The path contains no files. ERROR"

        # Check if more than one file exists
        if len(files) > 1:
            return "Only one file per path is allowed. ERROR"

        # Only one file exists
        file_name = files[0]
        _, ext = os.path.splitext(file_name)

        # Check allowed extensions
        if ext.lower() not in ['.txt', '.sql', '.csv']:
            return f"File format '{ext}' not allowed. Only .txt .sql or .csv files are accepted. ERROR"

        # Read and return the file content
        file_path = os.path.join(path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {e}"




@tool("DebugSQl", args_schema=debugSQl, return_direct=False)
def DebugSQLFunction(pipeline_name: str, user_requirement: str, test_case_name: str):
    """
    Use this tool to fix a sql process, 
    when teh user wants to fix some sql or code proccess based on 
    test case name and pipeline name, this tool will fix the sql automatically
    """
    
    agent = DataDebug(pipeline_name,user_requirement,test_case_name)

    response = agent.run()
    
    return response
