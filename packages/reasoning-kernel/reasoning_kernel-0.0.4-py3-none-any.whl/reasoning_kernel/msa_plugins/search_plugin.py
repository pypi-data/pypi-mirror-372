from semantic_kernel.functions.kernel_function_decorator import kernel_function

class SearchPlugin:
    """MSA Search as SK Plugin"""
    
    @kernel_function(
        description="Retrieve knowledge from the knowledge base",
        name="search_knowledge"
    )
    async def search_knowledge(self, context) -> str:
        query = context["query"]
        
        # Use SK's memory service for retrieval
        memory = context.kernel.memory
        
        # Search for relevant knowledge
        results = await memory.search_async("knowledge", query)
        
        return str(results)