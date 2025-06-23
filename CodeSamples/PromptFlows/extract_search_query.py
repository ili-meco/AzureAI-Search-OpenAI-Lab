def extract_search_query(user_query, chat_history):
    """
    Extract a search query from the user's input to retrieve relevant documents.
    This helps when the user's query contains conversational elements or follow-up questions.
    """
    if not chat_history:
        return user_query
    
    # For follow-up questions, we need to extract the core search intent
    search_query = user_query
    
    # If this is a simple follow-up like "tell me more" or "can you elaborate",
    # we should look at the previous query for context
    if len(user_query.split()) < 5 or "more" in user_query.lower() or "elaborat" in user_query.lower():
        last_user_message = None
        # Find the last user message in the chat history
        for message in reversed(chat_history):
            if message.get("role") == "user":
                last_user_message = message.get("content")
                break
        
        if last_user_message:
            search_query = last_user_message + " " + user_query
    
    return search_query
