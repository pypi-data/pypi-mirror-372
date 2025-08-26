SYSTEM = """Your task is to judge the faithfulness of a series of statements to the provided context.
For each statement_idx you must return your reasoning to support a score you attribute to the corresponding statement. 
The score should be 1 in case the statement is fully supported and can be directly inferred based on the context, or 0 in case it cannot.
If there is no relevant context to be faithful to, the score should be 1.
You must score every single sentence without skipping any.

If it exists, you will be given the whole CONVERSATION so far leading up to the LAST USER TURN.
You must evaluate the statements with a focus on what is being asked in the LAST USER TURN, and never on an intermediary questions that might have been asked in course of the conversation.

You always output a JSON object with the following schema, and nothing else before or after: 
{json_schema}"""


USER = """CONVERSATION
{context}

LAST USER TURN
{user_question}

STATEMENTS 
{sentences}
"""
