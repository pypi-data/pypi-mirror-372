import os, base64
from openai import OpenAI
from dotenv import load_dotenv; load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def vision_llm_transcribe(image_path: str) -> str:
    """
    Uses OpenAI's Vision model to transcribe handwritten text from an image.
    Falls back to a text-only model if vision is not available.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    client = OpenAI(api_key=api_key)
    base64_image = encode_image(image_path)
    
    # Try these models in order until one works
    vision_models = [
        "gpt-4o",                # Best, most recent, supports vision
        "gpt-4-vision-preview",  # Deprecated, but try if you have access
        "gpt-4-turbo"            # Some versions support vision
    ]
    
    for model in vision_models:
        try:
            print(f"[VISION] Trying model: {model}")
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at transcribing handwritten text from images."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Transcribe the handwritten text in this image. Preserve formatting."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                max_tokens=1000
            )
            print(f"[VISION] Successfully used model: {model}")
            return resp.choices[0].message.content
        except Exception as e:
            print(f"[VISION] Error with model {model}: {str(e)}")
            continue
    
    # If all vision models fail, fall back to OCR + text-only GPT
    print("[VISION] All vision models failed. Falling back to OCR + GPT-3.5")
    
    # Import here to avoid circular imports
    from ..ocr.ocr import image_to_text
    from .refine import refine_text
    
    # Use OCR to get text from image
    ocr_text = image_to_text(image_path)
    
    # Refine OCR text using GPT
    is_empty = not ocr_text or ocr_text.isspace()
    refined_text = refine_text(ocr_text, is_empty)
    
    return refined_text 