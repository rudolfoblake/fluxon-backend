class PromptBuilder:
    @staticmethod
    def extraction_prompt(text: str, field: str) -> str:
        return f"""
        Extract the information '{field}' from the following message.
        Message: {text}
        
        Return ONLY the value. If not found, return 'unknown'.
        """

    @staticmethod
    def qualification_prompt(text: str, media_info: str = "") -> str:
        return f"""
        Analyze the following WhatsApp message for lead qualification.
        Message: {text}
        {media_info}
        
        Extract:
        1. Buying Intent (high, medium, low)
        2. Urgency (high, medium, low)
        3. Main Pain Points
        4. Business Signals (e.g., mentions automation, scaling, budget)
        """

    @staticmethod
    def lead_summary_prompt(conversation_history: str) -> str:
        return f"""
        Summarize the key points of this lead based on the conversation:
        {conversation_history}
        """
