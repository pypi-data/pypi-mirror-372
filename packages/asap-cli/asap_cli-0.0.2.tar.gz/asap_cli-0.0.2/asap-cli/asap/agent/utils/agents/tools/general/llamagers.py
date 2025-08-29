import sys
import threading
import itertools
import boto3
from botocore.config import Config
from langchain_aws import ChatBedrockConverse

class BedrockLLamager:
    _instances = {}   # {name: BedrockLLamager}
    _lock = threading.Lock()

    def __init__(self, model: str = None):
        self._profiles = [
            "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        ]
        self._profile_cycle = itertools.cycle(self._profiles)
        self._clients = {}  
        self._active_profile = None  

        if model:
            if model not in self._profiles:
                raise ValueError(f"Model '{model}' is not in supported profiles: {self._profiles}")
            self._forced_profile = model
        else:
            self._forced_profile = None

        self._bedrock_config = Config(
            connect_timeout=120,
            read_timeout=120,
            retries={"max_attempts": 2}
        )
        self._bedrock_rt = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=self._bedrock_config
        )

    @classmethod
    def instance(cls, name: str = "default", model: str = None):
        """Get or create a named singleton instance."""
        if name not in cls._instances:
            with cls._lock:
                if name not in cls._instances:
                    cls._instances[name] = cls(model)
        return cls._instances[name]

    @classmethod
    def new_instance(cls, name: str, model: str = None):
        """Force creation of a NEW named instance, overwriting if exists."""
        with cls._lock:
            cls._instances[name] = cls(model)
        print(f"[BedrockLLamager] 🆕 Created new instance '{name}' with model: {model or 'rotation'}")
        return cls._instances[name]

    def _get_model_client(self, profile):
        if profile not in self._clients:
            client = ChatBedrockConverse(
                model=profile,
                temperature=0.1,
                max_tokens=65536,
                client=self._bedrock_rt
            )
            self._clients[profile] = {"client": client, "profile": profile}
        return self._clients[profile]

    def _next_client(self):
        if self._forced_profile:
            profile = self._forced_profile
        else:
            profile = next(self._profile_cycle)
        return self._get_model_client(profile)

    def call(self, messages):
        tried_profiles = set()

        while len(tried_profiles) < len(self._profiles):
            entry = self._next_client()
            client = entry["client"]
            profile = entry["profile"]

            if profile in tried_profiles:
                continue
            tried_profiles.add(profile)

            try:
                print(f"[BedrockLLamager] ▶️ Using model: {profile}")
                result = client.invoke(messages)
                self._active_profile = profile
                return result
            except Exception as e:
                print(f"[BedrockLLamager] ❌ Error with profile {profile}: {e}")
                if self._forced_profile:
                    raise  

        print("\n🚨 All Bedrock model profiles failed.\n")
        sys.exit(1)

    def set_model(self, model: str):
        if model not in self._profiles:
            raise ValueError(f"Model '{model}' is not in supported profiles: {self._profiles}")
        self._forced_profile = model
        self._active_profile = None
        print(f"[BedrockLLamager] 🔄 Model switched to: {model}")

    def get_model(self):
        if self._forced_profile:
            #print(f"[BedrockLLamager] 📌 Current pinned model: {self._forced_profile}")
            return self._get_model_client(self._forced_profile)["client"]

        if self._active_profile and self._active_profile in self._clients:
            print(f"[BedrockLLamager] 📌 Current active model: {self._active_profile}")
            return self._clients[self._active_profile]["client"]

        first_profile = self._profiles[0]
        self._active_profile = first_profile
        print(f"[BedrockLLamager] 📌 Defaulting to first model: {first_profile}")
        return self._get_model_client(first_profile)["client"]

# class BedrockLLamager:
#     _instance = None
#     _lock = threading.Lock()

#     def __init__(self, model: str = None):
#         self._profiles = [
#             "us.anthropic.claude-sonnet-4-20250514-v1:0",
#             "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
#         ]
#         self._profile_cycle = itertools.cycle(self._profiles)
#         self._clients = {}  # {profile_name: {"client": ChatBedrockConverse, "profile": str}}
#         self._active_profile = None  # track the last working profile

#         # If a model is explicitly provided, pin to that model
#         if model:
#             if model not in self._profiles:
#                 raise ValueError(f"Model '{model}' is not in supported profiles: {self._profiles}")
#             self._forced_profile = model
#         else:
#             self._forced_profile = None

#         self._bedrock_config = Config(
#             connect_timeout=120,
#             read_timeout=120,
#             retries={"max_attempts": 2}
#         )
#         self._bedrock_rt = boto3.client(
#             "bedrock-runtime",
#             region_name="us-east-1",
#             config=self._bedrock_config
#         )

#     @classmethod
#     def instance(cls, model: str = None):
#         """Get the singleton manager instance (optionally with a chosen model)."""
#         if cls._instance is None:
#             with cls._lock:
#                 if cls._instance is None:
#                     cls._instance = cls(model)
#         return cls._instance

#     def _get_model_client(self, profile):
#         """Get or create the model client for the given profile."""
#         if profile not in self._clients:
#             client = ChatBedrockConverse(
#                 model=profile,
#                 temperature=0.1,
#                 max_tokens=65536,
#                 client=self._bedrock_rt
#             )
#             self._clients[profile] = {
#                 "client": client,
#                 "profile": profile
#             }
#         return self._clients[profile]

#     def _next_client(self):
#         """Rotate to the next model profile or use the forced one."""
#         if self._forced_profile:
#             profile = self._forced_profile
#         else:
#             profile = next(self._profile_cycle)
#         return self._get_model_client(profile)

#     def call(self, messages):
#         """Try to invoke the current model, rotate if error occurs (unless forced)."""
#         tried_profiles = set()

#         while len(tried_profiles) < len(self._profiles):
#             entry = self._next_client()
#             client = entry["client"]
#             profile = entry["profile"]

#             if profile in tried_profiles:
#                 continue

#             tried_profiles.add(profile)

#             try:
#                 print(f"[BedrockLLamager] ▶️ Using model: {profile}")
#                 result = client.invoke(messages)
#                 self._active_profile = profile
#                 return result
#             except Exception as e:
#                 print(f"[BedrockLLamager] ❌ Error with profile {profile}: {e}")
#                 if self._forced_profile:
#                     # if user forced a profile, don't rotate
#                     raise
#                 # else try next

#         # All profiles failed — exit gracefully
#         print("\n🚨 All Bedrock model profiles failed.")
#         print("Please check your AWS credentials, network connection, and Bedrock model availability.")
#         print("The program will now exit.\n")
#         sys.exit(1)

#     def set_model(self, model: str):
#         """Force the manager to use a specific model at runtime."""
#         if model not in self._profiles:
#             raise ValueError(f"Model '{model}' is not in supported profiles: {self._profiles}")
#         self._forced_profile = model
#         self._active_profile = None  # reset so next call uses this
#         print(f"[BedrockLLamager] 🔄 Model switched to: {model}")

#     def get_model(self):
#         """
#         Return the ChatBedrockConverse client that was last working in `.call()`,
#         or the forced one if set.
#         """
#         if self._forced_profile:
#             print(f"[BedrockLLamager] 📌 Current pinned model: {self._forced_profile}")
#             return self._get_model_client(self._forced_profile)["client"]

#         if self._active_profile and self._active_profile in self._clients:
#             print(f"[BedrockLLamager] 📌 Current active model: {self._active_profile}")
#             return self._clients[self._active_profile]["client"]

#         first_profile = self._profiles[0]
#         self._active_profile = first_profile
#         print(f"[BedrockLLamager] 📌 Defaulting to first model: {first_profile}")
#         return self._get_model_client(first_profile)["client"]