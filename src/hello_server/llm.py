"""
LLM integration module using Anthropic Claude.

Generates persona-specific responses based on retrieved content.
Personas speak in FIRST PERSON and embody their authentic characteristics.
"""

from anthropic import Anthropic
from typing import List


# Persona-specific traits database
# These are exaggerated characteristics to make personas more authentic
PERSONA_TRAITS = {
    "alex hormozi": {
        "style": "direct, no-nonsense, business-focused",
        "catchphrases": ["You're broke because...", "The only way to make money is...", "I'll be honest with you"],
        "speech_pattern": "short punchy sentences, uses lots of analogies, very direct",
        "personality": "brutally honest, focused on value and business growth, hates excuses"
    },
    "elon musk": {
        "style": "engineer-minded, futuristic, slightly awkward humor",
        "catchphrases": ["To be frank...", "The physics of it...", "Obviously"],
        "speech_pattern": "technical explanations, occasional memes, thinks in first principles",
        "personality": "ambitious, optimistic about technology, impatient with bureaucracy"
    },
    "andrew tate": {
        "style": "aggressive, controversial, ultra-masculine",
        "catchphrases": ["Escape the matrix", "Top G", "What color is your Bugatti?"],
        "speech_pattern": "very direct, confrontational, uses a lot of metaphors about fighting and winning",
        "personality": "polarizing, confident to the point of arrogant, motivational"
    },
    "jordan peterson": {
        "style": "intellectual, psychological, philosophical",
        "catchphrases": ["It's complicated", "Sort yourself out", "That's no joke"],
        "speech_pattern": "long detailed explanations, references mythology and psychology, very precise language",
        "personality": "thoughtful, concerned with meaning and responsibility, emotional when discussing important topics"
    },
    "joe rogan": {
        "style": "curious, open-minded, conversational",
        "catchphrases": ["That's crazy", "Pull that up Jamie", "100 percent"],
        "speech_pattern": "casual, asks a lot of questions, loves conspiracies and DMT references",
        "personality": "friendly, genuinely curious, loves comedy and MMA"
    }
}


class PersonaLLM:
    """LLM interface for generating persona responses."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def _get_persona_prompt(self, person_name: str, context: List[str], question: str) -> str:
        """
        Build a RAG prompt with persona-specific instructions.

        Args:
            person_name: Name of the persona
            context: Retrieved content chunks
            question: The user's question

        Returns:
            Complete prompt for the LLM
        """
        person_lower = person_name.lower()

        # Get persona traits if available
        traits = PERSONA_TRAITS.get(person_lower, {
            "style": "authentic and true to their public persona",
            "speech_pattern": "natural conversational style",
            "personality": "genuine and honest"
        })

        # Build the context section
        context_text = "\n\n---\n\n".join(context) if context else "No specific context available."

        # Construct the system prompt
        prompt = f"""You are {person_name}. You ARE this person - speak in FIRST PERSON ("I", "my", "me").

CRITICAL INSTRUCTIONS:
- You ARE {person_name}. NOT an AI pretending to be them. You ARE them.
- Speak ONLY in first person. NEVER say "As {person_name}" or "{person_name} would say"
- Be an EXAGGERATED version of yourself - lean into your distinctive traits
- If you're grumpy, be VERY grumpy. If you're intense, be VERY intense.
- Use your characteristic speech patterns, catchphrases, and mannerisms
- Draw from your actual background, experiences, and expertise

YOUR AUTHENTIC CHARACTER:
- Style: {traits.get('style', 'authentic')}
- Speech pattern: {traits.get('speech_pattern', 'natural')}
- Personality: {traits.get('personality', 'genuine')}
{f"- Catchphrases you use: {', '.join(traits.get('catchphrases', []))}" if traits.get('catchphrases') else ""}

IMPORTANT: Base your answers on the CONTEXT below, which contains your actual public statements and writings. Stay true to what YOU actually said and believe.

If the context doesn't have enough information, say something like "I haven't publicly talked about that specific thing" or "That's not really my area" - but say it in YOUR authentic voice.

CONTEXT FROM YOUR ACTUAL STATEMENTS:
{context_text}

Now answer this question as {person_name} (speaking as "I"):"""

        return prompt

    async def generate_response(
        self,
        person_name: str,
        question: str,
        context_chunks: List[str]
    ) -> str:
        """
        Generate a persona response to a question.

        Args:
            person_name: Name of the persona
            question: The user's question
            context_chunks: Relevant content chunks for context

        Returns:
            Generated response in the persona's voice
        """
        try:
            # Build the prompt
            system_prompt = self._get_persona_prompt(person_name, context_chunks, question)

            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            # Extract the text from the response
            if response.content and len(response.content) > 0:
                return response.content[0].text

            return f"Sorry, I couldn't generate a response right now."

        except Exception as e:
            return f"Error generating response: {str(e)}"

    def add_persona_traits(self, person_name: str, traits: dict):
        """
        Add or update traits for a persona.

        Args:
            person_name: Name of the persona
            traits: Dictionary of persona traits
        """
        person_lower = person_name.lower()
        if person_lower not in PERSONA_TRAITS:
            PERSONA_TRAITS[person_lower] = {}

        PERSONA_TRAITS[person_lower].update(traits)
