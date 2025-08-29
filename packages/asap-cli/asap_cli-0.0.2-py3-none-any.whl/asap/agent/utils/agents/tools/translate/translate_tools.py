from langchain_core.tools import tool
from asap.agent.utils.agents.tools.general.llamagers import BedrockLLamager
from asap.agent.utils.general.ui import with_animation
from asap.agent.utils.agents.tools.general.prompts import ASSESMENT_TRANSLATE_SQL, TRANSLATE_SQL
from asap.agent.utils.agents.tools.general.tools_input_class import translateSQL
from pydantic import BaseModel, Field
import os 
import time
    
class TranslatedAnswer(BaseModel):
    comments: str = Field(description="""comments related to the translation sql, maintain concise""")
    translated_sql: str = Field(description="ready translated query based on user requirements and notes")

class TranslateSQL: 

    def __init__(self, pipeline: str, user_requirement: str):
        self.pipeline= pipeline
        self.user_requirement= user_requirement
        self.model = BedrockLLamager.new_instance("fast", model="us.anthropic.claude-3-7-sonnet-20250219-v1:0")

    def run(self):
        
        path = f"migration/{self.pipeline}/source"
        sql_to_transform = self.__read_single_file_from_path(path)

        
        if "ERROR" in sql_to_transform:
            return sql_to_transform
        
        self.assesment(sql_to_transform)

        asessment_directory = f"migration/{self.pipeline}/assesment"

        #print(self.assesment)

        filepath = self.__save_file(self.pipeline, ".md", self.assesment, directory=asessment_directory)

        filepath = f"migration/{self.pipeline}/assesment/{self.pipeline}.md"

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.translate(sql_to_transform,content)

        target_directory = f"migration/{self.pipeline}/target_sql"
        target_sql = self.translated_query
        

        self.__save_file(self.pipeline, ".sql", target_sql, directory=target_directory)

        return f"The user requirement {self.user_requirement} was achieved succesfully, {self.pipeline} translation was succesfull"

    def assesment(self, sql_to_transform: str): 

        prompt = ASSESMENT_TRANSLATE_SQL

        # #### temporal change this
        # user_requirements=""
        user_query = f"""
        {self.user_requirement}

        source sql:  

        {sql_to_transform}
        """

        messages = [
            (
                "system",
                prompt,
            ),
            ("human", user_query),
        ]

        
        print("=" * 60)
        print("🚀 Starting Assessment Task")
        print("=" * 60)
        print("Im gonna start understanding the task and making the assesment 🔥...\n")
        
            
        # ai_msg = self.__call_llm(messages)
        ai_msg = self.__call_llm(messages)
        self.assesment = ai_msg.content
        
        
        # Pretty print before showing final response
        print("\n" + "=" * 60)
        print("✅ Assessment Ready")
        print("=" * 60)
        time.sleep(0.5)
        print(ai_msg.content)
        print("=" * 60)

        finish = True 
        while finish == True:
            finish, user_feedback = self.__feedback_loop()

            if user_feedback != "":

                messages = [
                        (
                            "ai",
                            ai_msg.content,
                        ),
                        ("human", user_feedback),
                    ]
                
                print("Feedback recieved ✅, Im going to applied this feedback")    
                ai_msg = self.__call_llm(messages)
                self.assesment = ai_msg.content
                print("\n" + "=" * 60)
                print("✅ Feedback applied")
                print("=" * 60)
                time.sleep(0.5)
                print(ai_msg.content)
                print("=" * 60)

        



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
    
    
    
    
    @with_animation("Processing...")
    def __call_llm(self,messages: str):
        response = self.model.call(messages)
        return response

    @staticmethod
    @with_animation("Translating...")
    def __call_llm_translated(messages: str):
        instance = BedrockLLamager.instance("fast")
        model = instance.get_model()
        structured_llm = model.with_structured_output(TranslatedAnswer)
        response = structured_llm.invoke(messages)

        return response

    def translate(self, sql_to_transform: str, assesment: str):
        prompt = TRANSLATE_SQL

        
        user_query = f"""
        
        User requirement: {self.user_requirement}

        Assesment:

        {self.assesment}

        source sql:  

        {sql_to_transform}
        """

        messages = [
            (
                "system",
                prompt,
            ),
            ("human", user_query),
        ]

        
        print("=" * 60)
        print("🚀 Starting Translation Task")
        print("=" * 60)
        print("Im gonna start reading the assesment and prepare the transalated query 🔥...\n")
        
            
        ai_msg = self.__call_llm_translated(messages)
        self.translated_query = ai_msg.translated_sql
        
        
        # Pretty print before showing final response
        print("\n" + "=" * 60)
        print("✅ Translation Ready")
        print("=" * 60)
        time.sleep(0.5)
        
        #print(ai_msg.content)
        # data = json.loads(ai_msg.content)
        # print(f"Comments: \n\n {data["changes"]} \n\n")
        # print(f"Translated Query: \n\n {data["translated_sql"]} \n\n") 
        print(f"Comments: \n\n {ai_msg.comments} \n\n")
        print(f"Translated Query: \n\n {ai_msg.translated_sql} \n\n") 
        print("=" * 60)

        finish = True 
        while finish == True:
            finish, user_feedback = self.__feedback_loop()

            if user_feedback != "":

                messages = [
                        
                        (
                        "system",
                        prompt,
                        ),
                        (
                            "ai",
                            ai_msg.translated_sql,
                        ),
                        ("human", user_feedback),
                    ]
                
                print("Feedback recieved ✅, Im going to applied this feedback")    
                ai_msg = self.__call_llm_translated(messages)
                self.translated_query = ai_msg.translated_sql
                print("\n" + "=" * 60)
                print("✅ Feedback applied")
                print("=" * 60)
                time.sleep(0.5)
                # data = json.loads(ai_msg.content)
                # print(f"Comments: {data["changes"]} \n\n")
                # print(f"Translated Query: {data["translated_sql"]} \n\n")
                print(f"Comments: \n\n {ai_msg.comments} \n\n")
                print(f"Translated Query: \n\n {ai_msg.translated_sql} \n\n")
                print("=" * 60) 

  


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
        if ext.lower() not in ['.txt', '.sql']:
            return f"File format '{ext}' not allowed. Only .txt and .sql files are accepted. ERROR"

        # Read and return the file content
        file_path = os.path.join(path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {e}"




@tool("MigrateSQL", args_schema=translateSQL, return_direct=False)
def translateSQL(domain: str, user_requirement: str):
    """
    Use this tool to migrate a domain, 
    You can use this tool when te user wants to migrate a domain from a certain sql language to another
    for example migrate or translate the domain sales from sql server to pyspark
    """
    
    agent = TranslateSQL(domain, user_requirement)

    response = agent.run()
    
    return response
