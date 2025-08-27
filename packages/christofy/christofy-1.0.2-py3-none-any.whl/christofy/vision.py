"""
VisionSpell - Multimodal Vision Analysis with Ollama Integration

A focused vision-language system that uses any multimodal model available in Ollama
to perform natural language reasoning over images with conversation capabilities.
"""

import os
import platform
import requests
import json
import base64
import io
import time
import hashlib
import inspect
from pathlib import Path
from typing import Union, List, Optional, Dict, Any
import logging

__version__ = "1.0.2"
__author__ = "Aswin Christo"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for Pillow availability
try:
    from PIL import Image
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logger.warning("Vision support requires Pillow. Install with: pip install Pillow")

# ==================== CORE FUNCTIONS ====================

def get_ollama_base_url() -> str:
    """Get the appropriate Ollama base URL."""
    return os.getenv('OLLAMA_HOST', "http://localhost:11434")

def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    ollama_url = get_ollama_base_url()
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models.get('models', [])]
        return []
    except:
        return []

def get_vision_models() -> List[str]:
    """Get available vision-capable models."""
    all_models = get_available_models()
    vision_keywords = ['llava', 'bakllava', 'moondream', 'cogvlm', 'phi3-vision', 'minicpm']
    
    vision_models = []
    for model in all_models:
        if any(keyword in model.lower() for keyword in vision_keywords):
            vision_models.append(model)
    
    return vision_models

def validate_vision_model(model_name: str) -> bool:
    """Check if model supports vision capabilities."""
    vision_models = {
        'llava', 'llava:7b', 'llava:13b', 'llava:34b',
        'bakllava', 'bakllava:7b',
        'llava-phi3', 'llava-phi3:3.8b',
        'moondream', 'moondream:1.8b',
        'cogvlm', 'cogvlm:19b',
        'minicpm-v', 'minicpm-v:8b'
    }
    
    available_models = get_available_models()
    
    # Check exact match
    if model_name in available_models:
        return any(vision_model in model_name.lower() for vision_model in vision_models)
    
    # Check base model
    base_model = model_name.split(':')[0].lower()
    return base_model in {vm.split(':')[0] for vm in vision_models}

def get_fallback_vision_model() -> str:
    """Get the best available vision model."""
    available = get_available_models()
    
    # Preferred order
    fallback_order = ['llava:7b', 'llava', 'bakllava:7b', 'bakllava', 'moondream', 'minicpm-v']
    
    for model in fallback_order:
        if model in available:
            return model
        # Check variants
        for available_model in available:
            if available_model.startswith(model.split(':')[0]):
                return available_model
    
    raise Exception("No vision-capable models found. Install with: ollama pull llava")

def process_image(image_path: Union[str, Path]) -> str:
    """Process and encode image for Ollama."""
    if not VISION_AVAILABLE:
        raise ImportError("Vision support requires Pillow. Install with: pip install Pillow")
    
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Supported formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    if path.suffix.lower() not in supported_formats:
        raise ValueError(f"Unsupported format: {path.suffix}. Supported: {', '.join(supported_formats)}")
    
    try:
        with Image.open(path) as img:
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
                logger.info(f"🔄 Converted image mode from {Image.open(path).mode} to RGB")
            
            # Resize if too large (optimization)
            max_size = (1024, 1024)
            original_size = img.size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"📐 Resized image from {original_size} to {img.size}")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            
        return base64.b64encode(image_bytes).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise

def show_vision_spell_help():
    """Show detailed help for vision_spell function."""
    help_text = """
🔮 VISION_SPELL FUNCTION HELP

SIGNATURE:
vision_spell(
    image_path: Union[str, Path],
    question: str,
    model: str = "llava",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    conversation_mode: bool = False
) -> Union[str, 'VisionConversation']

PARAMETERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 image_path (required)
   Path to your image file
   Supported formats: .jpg, .jpeg, .png, .bmp, .gif, .webp
   Example: "photo.jpg", "/path/to/image.png"

❓ question (required)  
   Your question about the image
   Example: "What do you see?", "Describe this image"

🤖 model (default: "llava")
   Vision-capable Ollama model to use
   Options: llava, llava:7b, llava:13b, bakllava, moondream
   Example: "llava:13b"

🌡️  temperature (default: 0.7)
   Response creativity level (0.0 to 1.0)
   Lower = more factual, Higher = more creative
   Example: 0.1 (very factual), 0.9 (very creative)

📏 max_tokens (optional)
   Maximum length of response
   Example: 500, 1000

💬 system_prompt (optional)
   Custom instructions for the AI
   Example: "You are a medical expert analyzing X-rays"

🔄 conversation_mode (default: False)
   Return VisionConversation object for follow-up questions
   Set to True for multi-turn conversations

RETURN VALUE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
str: AI's answer to your question
VisionConversation: Chat object (if conversation_mode=True)

EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Simple analysis
result = vision_spell("photo.jpg", "What do you see?")

# High-precision medical analysis  
result = vision_spell(
    "xray.jpg", 
    "Are there any fractures?",
    model="llava:13b",
    temperature=0.1
)

# Conversation mode
chat = vision_spell(
    "diagram.png",
    "Explain this flowchart", 
    conversation_mode=True
)
response1 = chat.ask("What's the first step?")
response2 = chat.ask("What happens after that?")
"""
    print(help_text)

# ==================== MAIN VISION FUNCTION ====================

def vision_spell(
    image_path: Union[str, Path] = None,
    question: str = None,
    model: str = "llava",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    conversation_mode: bool = False
) -> Union[str, 'VisionConversation']:
    """
    🔮 Analyze images and answer questions using multimodal AI models.
    
    Args:
        image_path: Path to the image file (.jpg, .png, .bmp, .gif, .webp)
        question: Your question about the image  
        model: Vision-capable Ollama model (default: "llava")
        temperature: Response creativity (0.0-1.0, default: 0.7)
        max_tokens: Maximum response length (optional)
        system_prompt: Custom system instructions (optional)
        conversation_mode: Return chat object for follow-ups (default: False)
    
    Returns:
        str: AI's answer (normal mode)
        VisionConversation: Chat object (conversation mode)
    
    Examples:
        # Simple analysis
        result = vision_spell("photo.jpg", "What do you see?")
        
        # Medical analysis with high precision
        result = vision_spell("xray.jpg", "Any abnormalities?", model="llava:13b", temperature=0.1)
        
        # Start conversation
        chat = vision_spell("diagram.png", "Explain this", conversation_mode=True)
        chat.ask("What's the main component?")
    """
    
    # Show help if called without arguments or with ??
    if image_path is None and question is None:
        show_vision_spell_help()
        return
    
    # Handle ?? help syntax
    frame = inspect.currentframe().f_back
    if frame and 'vision_spell??' in str(frame.f_code):
        show_vision_spell_help()
        return
    
    # Validate inputs
    if not image_path:
        raise ValueError("image_path is required")
    if not question:
        raise ValueError("question is required")
    
    if not VISION_AVAILABLE:
        raise ImportError("Vision support requires Pillow. Install with: pip install Pillow")
    
    try:
        logger.info(f"🔮 Starting VisionSpell with model: {model}")
        
        # Validate and process image
        image_data = process_image(image_path)
        logger.info(f"📸 Processed image: {Path(image_path).name}")
        
        # Check model availability and vision support
        if not validate_vision_model(model):
            available_vision = get_vision_models()
            if available_vision:
                fallback_model = available_vision[0]
                logger.warning(f"🔄 Model '{model}' not available, using: {fallback_model}")
                model = fallback_model
            else:
                raise Exception("No vision models available. Install with: ollama pull llava")
        
        # Return conversation object if requested
        if conversation_mode:
            return VisionConversation(
                image_path=image_path,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                initial_question=question
            )
        
        # Build message
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": question,
            "images": [image_data]
        })
        
        # Generate response
        ollama_url = get_ollama_base_url()
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}
        
        logger.info(f"🤖 Generating response...")
        response = requests.post(
            f"{ollama_url}/api/chat",
            json=payload,
            timeout=180
        )
        
        if response.status_code != 200:
            error_msg = f"Ollama API error: {response.status_code}"
            try:
                error_detail = response.json().get('error', '')
                if error_detail:
                    error_msg += f" - {error_detail}"
            except:
                pass
            raise Exception(error_msg)
        
        result = response.json()
        answer = result.get('message', {}).get('content', 'No response generated')
        
        logger.info("✅ Vision analysis complete!")
        return answer
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Cannot connect to Ollama at {get_ollama_base_url()}. Is Ollama running?")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out. Try a simpler question or smaller image.")
    except Exception as e:
        logger.error(f"❌ VisionSpell error: {e}")
        raise

# ==================== CONVERSATION CLASS ====================

class VisionConversation:
    """
    Maintain conversation context for follow-up questions about an image.
    
    Usage:
        chat = vision_spell("image.jpg", "What is this?", conversation_mode=True)
        response1 = chat.ask("What colors do you see?")  
        response2 = chat.ask("Is this outdoors?")
        print(chat.summary())
    """
    
    def __init__(
        self, 
        image_path: Union[str, Path], 
        model: str = "llava",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        initial_question: Optional[str] = None
    ):
        self.image_path = Path(image_path)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.history = []
        self.image_data = process_image(image_path)
        
        logger.info(f"💬 Started conversation with {self.image_path.name} using {self.model}")
        
        # Process initial question if provided
        if initial_question:
            initial_response = self._query(initial_question, is_first=True)
            self.history.append({
                "question": initial_question,
                "answer": initial_response,
                "timestamp": time.time()
            })
    
    def ask(self, question: str) -> str:
        """
        Ask a follow-up question about the image.
        
        Args:
            question: Your follow-up question
            
        Returns:
            AI's response to your question
            
        Example:
            response = chat.ask("What material is this made of?")
        """
        try:
            answer = self._query(question)
            
            # Store in history
            self.history.append({
                "question": question,
                "answer": answer,
                "timestamp": time.time()
            })
            
            return answer
            
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            raise
    
    def _query(self, question: str, is_first: bool = False) -> str:
        """Internal method to query the model with conversation context."""
        messages = []
        
        # Add system prompt
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add conversation history
        for exchange in self.history:
            messages.append({
                "role": "user",
                "content": exchange["question"],
                "images": [self.image_data] if not messages or is_first else None
            })
            messages.append({
                "role": "assistant",
                "content": exchange["answer"]
            })
        
        # Add current question
        messages.append({
            "role": "user", 
            "content": question,
            "images": [self.image_data] if not self.history and not messages else None
        })
        
        # Generate response
        ollama_url = get_ollama_base_url()
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": self.temperature
        }
        
        if self.max_tokens:
            payload["options"] = {"num_predict": self.max_tokens}
        
        response = requests.post(
            f"{ollama_url}/api/chat",
            json=payload,
            timeout=180
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code}")
        
        result = response.json()
        return result.get('message', {}).get('content', 'No response')
    
    def summary(self) -> str:
        """
        Get a summary of the conversation.
        
        Returns:
            Formatted conversation summary
        """
        if not self.history:
            return f"📸 Image: {self.image_path.name}\n🤖 Model: {self.model}\n💬 No conversation yet."
        
        summary = f"📸 Image: {self.image_path.name}\n"
        summary += f"🤖 Model: {self.model}\n"
        summary += f"💬 Exchanges: {len(self.history)}\n"
        summary += f"⏱️  Started: {time.ctime(self.history[0]['timestamp'])}\n\n"
        
        for i, exchange in enumerate(self.history, 1):
            summary += f"Q{i}: {exchange['question']}\n"
            answer_preview = exchange['answer'][:150]
            if len(exchange['answer']) > 150:
                answer_preview += "..."
            summary += f"A{i}: {answer_preview}\n\n"
        
        return summary
    
    def export_conversation(self, format: str = "json") -> Union[str, Dict]:
        """
        Export conversation in different formats.
        
        Args:
            format: 'json', 'txt', or 'dict'
            
        Returns:
            Conversation data in requested format
        """
        data = {
            "image_path": str(self.image_path),
            "model": self.model,
            "temperature": self.temperature,
            "conversation": self.history,
            "summary_stats": {
                "total_exchanges": len(self.history),
                "start_time": self.history[0]["timestamp"] if self.history else None,
                "end_time": self.history[-1]["timestamp"] if self.history else None
            }
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2)
        elif format.lower() == "dict":
            return data
        elif format.lower() == "txt":
            return self.summary()
        else:
            raise ValueError("Format must be 'json', 'txt', or 'dict'")

# ==================== UTILITY FUNCTIONS ====================

def batch_vision_analysis(
    image_paths: List[Union[str, Path]],
    questions: Union[str, List[str]],
    model: str = "llava",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Analyze multiple images with questions.
    
    Args:
        image_paths: List of image file paths
        questions: Single question for all images, or list of questions
        model: Vision model to use
        temperature: Response creativity
        max_tokens: Maximum response length
        
    Returns:
        List of analysis results
        
    Example:
        results = batch_vision_analysis(
            ["img1.jpg", "img2.png"], 
            "What do you see?",
            model="llava:7b"
        )
    """
    if isinstance(questions, str):
        questions = [questions] * len(image_paths)
    
    if len(questions) != len(image_paths):
        raise ValueError("Number of questions must match number of images")
    
    results = []
    
    for i, (img_path, question) in enumerate(zip(image_paths, questions)):
        try:
            logger.info(f"📸 Analyzing {i+1}/{len(image_paths)}: {Path(img_path).name}")
            
            answer = vision_spell(
                image_path=img_path,
                question=question,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            results.append({
                "image_path": str(img_path),
                "question": question,
                "answer": answer,
                "status": "success",
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Failed to analyze {img_path}: {e}")
            results.append({
                "image_path": str(img_path),
                "question": question,
                "answer": None,
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            })
    
    return results

def get_system_info() -> Dict[str, Any]:
    """Get system information and model availability."""
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "visionspell_version": __version__,
        "ollama_url": get_ollama_base_url(),
        "features": {
            "vision_support": VISION_AVAILABLE,
            "ollama_connected": bool(get_available_models())
        },
        "models": {
            "all_available": get_available_models(),
            "vision_capable": get_vision_models()
        },
        "supported_formats": ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
    }

def list_vision_models():
    """Print available vision models in a nice format."""
    vision_models = get_vision_models()
    
    print("🤖 AVAILABLE VISION MODELS")
    print("=" * 40)
    
    if vision_models:
        for i, model in enumerate(vision_models, 1):
            print(f"{i:2d}. {model}")
        
        print(f"\n✅ Found {len(vision_models)} vision-capable models")
        print(f"🔧 Usage: vision_spell('image.jpg', 'question', model='{vision_models[0]}')")
    else:
        print("❌ No vision models found!")
        print("📥 Install vision models:")
        print("   ollama pull llava")
        print("   ollama pull bakllava")
        print("   ollama pull moondream")

# ==================== MODULE INFO ====================

def show_module_info():
    """Show module information and quick start guide."""
    info = f"""
🔮 VisionSpell v{__version__} by {__author__}

QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from christofy import vision_spell

# Simple analysis
result = vision_spell("photo.jpg", "What do you see?")

# Advanced analysis  
result = vision_spell(
    "medical.jpg", 
    "Any abnormalities?",
    model="llava:13b", 
    temperature=0.1
)

# Conversation mode
chat = vision_spell("diagram.png", "Explain this", conversation_mode=True)
chat.ask("What's the main component?")
chat.ask("How does it work?")

HELP & DOCUMENTATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
vision_spell()          # Show parameter help
list_vision_models()    # Show available models
get_system_info()       # System information

Vision Support: {'✅' if VISION_AVAILABLE else '❌'}
Ollama Connected: {'✅' if get_available_models() else '❌'}
Vision Models: {len(get_vision_models())}
"""
    print(info)

# ==================== ALIASES & EXPORTS ====================

# Main function alias
vision = vision_spell

# Export key functions
__all__ = [
    'vision_spell',
    'vision', 
    'VisionConversation',
    'batch_vision_analysis',
    'get_vision_models',
    'list_vision_models',
    'get_system_info',
    'show_module_info'
]

# Show info when imported
if __name__ != "__main__":
    show_module_info()
