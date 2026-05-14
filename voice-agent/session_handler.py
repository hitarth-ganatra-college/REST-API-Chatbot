import asyncio
import tempfile
import soundfile as sf
from config import Config
from db_helper import ChatTurn, insert_turn, next_turn_index
from stt_engine import stt_whisper
from chatbot_helper import get_bot_reply
from webrtc_peer import consume_audio

async def on_audio_chunk(audio_pcm_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        # Verify sample rate/channel to match your browser!
        sf.write(f, audio_pcm_bytes, 16000, subtype='PCM_16')
        audio_path = f.name

    transcript, confidence = stt_whisper(audio_path)
    turn_idx = next_turn_index(Config.SESSION_ID)
    turn = ChatTurn(
        session_id=Config.SESSION_ID,
        tenant_id=Config.TENANT_ID,
        outlet_id=Config.OUTLET_ID,
        user_id=Config.USER_ID,
        turn_index=turn_idx,
        speaker="user",
        msg_txt=transcript,
        stt_confidence=confidence
    )
    insert_turn(turn)

    bot_reply = await get_bot_reply(transcript)
    turn_idx += 1
    bot_turn = ChatTurn(
        session_id=Config.SESSION_ID,
        tenant_id=Config.TENANT_ID,
        outlet_id=Config.OUTLET_ID,
        user_id=Config.USER_ID,
        turn_index=turn_idx,
        speaker="bot",
        msg_txt=bot_reply
    )
    insert_turn(bot_turn)
    print(f"[{turn_idx}] Bot says: {bot_reply}")

def run():
    asyncio.run(consume_audio(on_audio_chunk))