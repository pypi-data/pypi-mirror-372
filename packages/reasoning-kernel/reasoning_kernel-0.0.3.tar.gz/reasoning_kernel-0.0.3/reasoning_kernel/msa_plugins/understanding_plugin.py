from semantic_kernel.functions.kernel_function_decorator import kernel_function

class UnderstandingPlugin:
    """MSA Understanding as SK Plugin"""
    
    @kernel_function(
        description="Parse and comprehend the scenario",
        name="understand_scenario"
    )
    async def understand_scenario(self, context) -> str:
        scenario = context["scenario"]
        
        # Use SK's AI service for generation
        ai_service = context.kernel.get_chat_service()
        
        # Generate understanding
        prompt = self._build_understanding_prompt(scenario)
        response = await ai_service.complete_async(prompt)
        
        return response

    def _build_understanding_prompt(self, scenario: str) -> str:
        """Builds the prompt for the understanding LLM."""
        return f"Extract the key entities and relationships from the following scenario:\n\n{scenario}"