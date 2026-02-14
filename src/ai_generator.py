import os
import random
try:
    from groq import Groq
except ImportError:
    Groq = None
from src.utils import setup_logger

logger = setup_logger('ai_generator')

class AICommentGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key and Groq:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        self.backup_templates = [
            "Great post! Thanks for sharing.",
            "Love this content!",
            "This is really interesting.",
            "Awesome shot!",
            "Totally agree with this.",
            "Keep up the great work!",
            "Saving this for later.",
            "So true!",
            "This is inspiring.",
            "Nice perspective!"
        ]

    def generate_comment(self, caption, context_info=None):
        """
        Generate a relevant comment based on the caption using Groq API.
        Falls back to templates if API fails or is not configured.
        """
        if not self.client:
            logger.warning("Groq client not initialized. Using backup template.")
            return random.choice(self.backup_templates)

        if not caption:
             return random.choice(self.backup_templates)

        try:
            prompt = f"""
            You are a friendly Instagram user. Write a short, engaging, and relevant comment (max 15 words) for this Instagram post caption. 
            Sound human, casual, and positive. Do not use hashtags. Do not sound like a bot.
            
            Caption: "{caption}"
            """
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=30,
            )
            
            comment = chat_completion.choices[0].message.content.strip().replace('"', '')
            logger.info(f"Generated AI comment: {comment}")
            return comment
            
        except Exception as e:
            logger.error(f"Error generating AI comment: {e}")
            return random.choice(self.backup_templates)

if __name__ == "__main__":
    # Test
    gen = AICommentGenerator()
    print(gen.generate_comment("Just finished a 5k run! Feeling great but tired. #fitness"))
