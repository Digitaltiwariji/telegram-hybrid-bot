async def search_dialogs_by_name(client, query: str, limit: int = 30):
    q = query.lower()
    results = []
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if q in name.lower():
            results.append(dialog)
            if len(results) >= limit:
                break
    return results

async def get_entity_by_id(client, chat_id: str):
    try:
        return await client.get_entity(int(chat_id))
    except Exception:
        return None

async def get_recent_forwardable(client, entity, limit: int = 10):
    # Check protected content at chat level
    if getattr(entity, 'noforwards', False):
        return None
    async for msg in client.iter_messages(entity, limit=limit):
        if msg and not getattr(msg, 'noforwards', False):
            return msg
    return None