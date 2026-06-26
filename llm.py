import anthropic
import config


client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def get_response(system_prompt: str, conversation_history: list[dict]) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        system=system_prompt,
        messages=conversation_history,
    )
    return response.content[0].text
