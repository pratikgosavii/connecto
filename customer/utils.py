# chat/utils.py
def generate_channel_id(user1_id, user2_id):
    ids = sorted([str(user1_id), str(user2_id)])
    return f"chat-{ids[0]}-{ids[1]}"
