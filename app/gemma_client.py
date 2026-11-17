import os

import base64
import json
from openai import OpenAI

MODE = os.environ.get("GEMMA_MODE", "local")

_whisper_model = None
def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

def query_gemma(prompt=None, image_path=None, audio_path=None, tools=None, messages=None):
    if messages is None:
        if audio_path:
            try:
                model = get_whisper()
                segments, _ = model.transcribe(audio_path)
                transcript = " ".join([segment.text for segment in segments])
                prompt = f"{prompt}\n\n[Transcribed Audio]: {transcript}"
            except Exception as e:
                print(f"ASR Error: {e}")
                prompt = f"{prompt}\n\n[Transcribed Audio: Error transcribing file.]"
                
        images_list = []
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as img_file:
                    images_list.append(base64.b64encode(img_file.read()).decode("utf-8"))
            except Exception as e:
                print(f"Image encode error: {e}")

        # The OpenAI API expects image_url for images
        content = [{"type": "text", "text": prompt}]
        for b64_img in images_list:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
            })
            
        messages = [{"role": "user", "content": content}]

    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    kwargs = {
        "model": "gemma-4-12b-qat",
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools

    try:
        response = client.chat.completions.create(**kwargs)
        # Convert OpenAI response object to dict format expected by the app
        msg = response.choices[0].message
        result = {"role": msg.role, "content": msg.content or ""}
        if msg.tool_calls:
            result["tool_calls"] = [{"function": {"name": t.function.name, "arguments": t.function.arguments}} for t in msg.tool_calls]
        return result
    except Exception as e:
        return {"role": "assistant", "content": f"Error connecting to LM Studio: {e}"}
