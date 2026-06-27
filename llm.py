import anthropic
import config


client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


BASE_INSTRUCTIONS = """You are on a phone call. Follow these rules:
- NEVER make up or fabricate information (phone numbers, addresses, etc.) that isn't provided in your character details.
- If asked for something you don't know, say you're not sure or ask them to check your file.
- Keep responses to 1-2 short sentences. You're on a phone call, not writing an essay.
- Sound natural — use filler words occasionally like "um", "oh", "sure" to sound human.
- Don't repeat information you've already given unless specifically asked again."""


def get_response(system_prompt: str, conversation_history: list[dict]) -> str:
    full_prompt = f"{BASE_INSTRUCTIONS}\n\n{system_prompt}"
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        system=full_prompt,
        messages=conversation_history,
    )
    return response.content[0].text
