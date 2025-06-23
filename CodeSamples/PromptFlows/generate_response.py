def generate_response(user_query, retrieved_documents, chat_history):
    """
    Generate a response using Azure OpenAI with retrieved documents as context.
    """
    import os
    # Note: In an actual prompt flow, this would use promptflow.connections
    # For this lab example, we'll use the Azure OpenAI SDK directly
    from openai import AzureOpenAI
    
    # Initialize OpenAI connection
    aoai_connection = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    # Prepare system message with context from retrieved documents
    system_message = "You are an AI assistant that helps answer questions about Azure AI Search. "
    system_message += "Base your answers on the following retrieved documents and cite your sources:\n\n"
    
    # Include retrieved documents in the system message
    for i, doc in enumerate(retrieved_documents, 1):
        system_message += f"Document {i}: {doc['title']}\n"
        system_message += f"Content: {doc['content']}\n\n"
    
    # Add citation instructions
    system_message += "\nWhen responding, please include citations to the relevant documents in your answer using [Document X] format."
    
    # Prepare messages for the API call
    messages = [
        {"role": "system", "content": system_message},
    ]
    
    # Add chat history if available
    if chat_history:
        for message in chat_history:
            messages.append(message)
    
    # Add current user query
    messages.append({"role": "user", "content": user_query})
    
    # Call Azure OpenAI
    response = aoai_connection.chat.completions.create(
        model=os.environ.get("GPT_MODEL_DEPLOYMENT"),
        messages=messages,
        temperature=0.5,
        max_tokens=800
    )
    
    return response.choices[0].message.content
