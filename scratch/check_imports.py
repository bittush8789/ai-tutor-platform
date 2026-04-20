import sys
try:
    from langchain.memory import ConversationBufferMemory
    print("langchain.memory: Success")
except Exception as e:
    print(f"langchain.memory: {e}")

try:
    from langchain_community.memory import ConversationBufferMemory
    print("langchain_community.memory: Success")
except Exception as e:
    print(f"langchain_community.memory: {e}")

try:
    from langchain.memory.buffer import ConversationBufferMemory
    print("langchain.memory.buffer: Success")
except Exception as e:
    print(f"langchain.memory.buffer: {e}")

import langchain
print(f"Langchain file: {langchain.__file__}")
