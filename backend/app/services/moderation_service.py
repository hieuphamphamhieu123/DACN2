"""
Content Moderation Service using AI Models
This service provides text and image moderation capabilities using pre-trained models
"""
from typing import Dict, Optional
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from PIL import Image
import io
import httpx
import logging

logger = logging.getLogger(__name__)


class ContentModerationService:
    """
    Service for moderating text content using Toxicity Detection Model
    Model: unitary/toxic-bert (Toxic comment classification)
    """

    def __init__(self):
        try:
            print("=" * 60)
            print("LOADING AI TEXT MODERATION MODEL...")
            print("=" * 60)
            logger.info("=" * 60)
            logger.info("LOADING AI TEXT MODERATION MODEL...")
            logger.info("=" * 60)

            # Load toxicity detection model
            self.model_name = "unitary/toxic-bert"
            print(f"Model: {self.model_name}")
            print("Downloading/Loading tokenizer...")
            logger.info(f"Model: {self.model_name}")
            logger.info("Downloading/Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            print("Downloading/Loading model weights...")
            logger.info("Downloading/Loading model weights...")
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

            # Create pipeline for easier inference
            device = 0 if torch.cuda.is_available() else -1
            print(f"Device: {'GPU (CUDA)' if device == 0 else 'CPU'}")
            logger.info(f"Device: {'GPU (CUDA)' if device == 0 else 'CPU'}")

            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                top_k=None,
                device=device
            )

            # Toxicity labels from toxic-bert
            self.toxic_labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

            print("=" * 60)
            print("TOXICITY DETECTION MODEL READY!")
            print(f"   - Model: {self.model_name}")
            print(f"   - Labels: {', '.join(self.toxic_labels)}")
            print(f"   - Type: Transformer-based BERT model (TRAINED ML MODEL)")
            print("=" * 60)
            logger.info("=" * 60)
            logger.info("✅ TOXICITY DETECTION MODEL READY!")
            logger.info(f"   - Model: {self.model_name}")
            logger.info(f"   - Labels: {', '.join(self.toxic_labels)}")
            logger.info(f"   - Type: Transformer-based BERT model (TRAINED ML MODEL)")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ Failed to load toxicity model: {e}")
            logger.warning("⚠️  Falling back to rule-based detection (NOT ML)")
            self.classifier = None
            self._init_fallback()

    def _init_fallback(self):
        """Initialize fallback rule-based detection"""
        self.toxic_keywords = [
            'fuck', 'shit', 'damn', 'bitch', 'asshole', 'bastard',
            'idiot', 'stupid', 'dumb', 'moron', 'kill yourself'
        ]

    async def moderate_text(self, text: str) -> Dict:
        """
        Moderate text content for toxic, spam, and hate speech

        Args:
            text: The text content to moderate

        Returns:
            Dictionary containing moderation results
        """
        if not text or len(text.strip()) == 0:
            return {
                "is_toxic": False,
                "is_spam": False,
                "is_hate_speech": False,
                "confidence_score": 0.0,
                "details": "empty content"
            }

        # If model loaded successfully, use AI detection
        if self.classifier is not None:
            try:
                return await self._ai_moderate_text(text)
            except Exception as e:
                logger.error(f"AI moderation failed: {e}, falling back to rules")
                return self._fallback_moderate_text(text)
        else:
            # Use fallback rule-based detection
            return self._fallback_moderate_text(text)

    async def _ai_moderate_text(self, text: str) -> Dict:
        """AI-based text moderation using toxic-bert"""
        print("Using TRAINED ML MODEL (toxic-bert) for text moderation")
        print(f"Text length: {len(text)} characters")
        logger.info("Using TRAINED ML MODEL (toxic-bert) for text moderation")
        logger.info(f"Text length: {len(text)} characters")

        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
            print(f"Truncated to {max_length} characters")
            logger.info(f"Truncated to {max_length} characters")

        # Get predictions from TRAINED MODEL
        print("Running inference on neural network...")
        logger.info("Running inference on neural network...")
        results = self.classifier(text)
        print(f"ML Model prediction complete!")
        logger.info(f"ML Model prediction complete!")

        # Parse results
        scores = {}
        for result in results[0]:
            label = result['label'].lower()
            score = result['score']
            scores[label] = score

        # Determine toxicity
        toxic_score = scores.get('toxic', 0.0)
        severe_toxic_score = scores.get('severe_toxic', 0.0)
        obscene_score = scores.get('obscene', 0.0)
        threat_score = scores.get('threat', 0.0)
        insult_score = scores.get('insult', 0.0)
        identity_hate_score = scores.get('identity_hate', 0.0)

        # Thresholds
        toxic_threshold = 0.5
        severe_threshold = 0.3

        is_toxic = (toxic_score > toxic_threshold or
                   obscene_score > toxic_threshold or
                   insult_score > toxic_threshold)

        is_hate_speech = (identity_hate_score > toxic_threshold or
                         severe_toxic_score > severe_threshold or
                         threat_score > toxic_threshold)

        # Simple spam detection (still rule-based)
        is_spam = self._check_spam(text)

        # Get max confidence
        confidence_score = max(
            toxic_score, severe_toxic_score, obscene_score,
            threat_score, insult_score, identity_hate_score
        )

        # Log ML model scores
        print("ML MODEL PREDICTION SCORES (from neural network):")
        print(f"   - Toxic: {toxic_score:.4f}")
        print(f"   - Severe Toxic: {severe_toxic_score:.4f}")
        print(f"   - Obscene: {obscene_score:.4f}")
        print(f"   - Threat: {threat_score:.4f}")
        print(f"   - Insult: {insult_score:.4f}")
        print(f"   - Identity Hate: {identity_hate_score:.4f}")
        logger.info("ML MODEL PREDICTION SCORES (from neural network):")
        logger.info(f"   - Toxic: {toxic_score:.4f}")
        logger.info(f"   - Severe Toxic: {severe_toxic_score:.4f}")
        logger.info(f"   - Obscene: {obscene_score:.4f}")
        logger.info(f"   - Threat: {threat_score:.4f}")
        logger.info(f"   - Insult: {insult_score:.4f}")
        logger.info(f"   - Identity Hate: {identity_hate_score:.4f}")
        logger.info(f"   - Max Confidence: {confidence_score:.4f}")

        # Generate details
        details = []
        if toxic_score > toxic_threshold:
            details.append(f"toxic language (ML confidence: {toxic_score:.2f})")
        if obscene_score > toxic_threshold:
            details.append(f"obscene content (ML confidence: {obscene_score:.2f})")
        if insult_score > toxic_threshold:
            details.append(f"insults detected (ML confidence: {insult_score:.2f})")
        if identity_hate_score > toxic_threshold:
            details.append(f"hate speech (ML confidence: {identity_hate_score:.2f})")
        if threat_score > toxic_threshold:
            details.append(f"threats detected (ML confidence: {threat_score:.2f})")
        if is_spam:
            details.append("spam patterns detected")

        print(f"Final Decision: {'BLOCK' if (is_toxic or is_hate_speech) else 'APPROVE'}")
        logger.info(f"Final Decision: {'BLOCK' if (is_toxic or is_hate_speech) else 'APPROVE'}")

        return {
            "is_toxic": is_toxic,
            "is_spam": is_spam,
            "is_hate_speech": is_hate_speech,
            "confidence_score": float(confidence_score),
            "details": ", ".join(details) if details else "content appears safe"
        }

    def _check_spam(self, text: str) -> bool:
        """Enhanced spam detection including gibberish/nonsense text"""
        import re

        print(f"[SPAM CHECK] Checking text: '{text}' (length: {len(text)})")

        # Traditional spam patterns
        spam_patterns = [
            r'(buy now|click here|limited offer|act fast)',
            r'(www\.|http|\.com){3,}',
            r'([A-Z]{5,}.*){3,}',
            r'(\$\$\$|!!!){3,}'
        ]
        text_lower = text.lower()

        # Check traditional spam patterns
        if any(re.search(pattern, text_lower) for pattern in spam_patterns):
            return True

        # NEW: Detect gibberish/random text
        # Remove spaces and count only alphabetic characters
        clean_text = re.sub(r'[^a-zA-Z]', '', text)

        # Skip if too short, but allow checking for very short meaningless strings
        if len(clean_text) < 3:
            return False

        # Pattern 1: High ratio of consonants (no vowels)
        vowels = 'aeiouàáảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoòóỏõọôồốổỗộơờớởỡợuùúủũụưừứửữựyỳýỷỹỵ'
        consonant_count = sum(1 for c in clean_text.lower() if c.isalpha() and c not in vowels)
        vowel_count = sum(1 for c in clean_text.lower() if c in vowels)

        # If more than 70% consonants → likely gibberish (lowered from 80%)
        if len(clean_text) > 0:
            consonant_ratio = consonant_count / len(clean_text)
            # For short text (3-8 chars), use 70% threshold
            # For longer text (8+ chars), use 75% threshold
            threshold = 0.70 if len(clean_text) < 8 else 0.75
            if consonant_ratio > threshold:
                print(f"SPAM DETECTED: High consonant ratio ({consonant_ratio:.2f}, threshold={threshold})")
                return True

        # Pattern 2: Mixed numbers and letters randomly (e.g., àle12321, abc123xyz456)
        mixed_pattern = re.search(r'[a-zA-Z]+\d+[a-zA-Z]*\d+', text)
        if mixed_pattern and len(re.findall(r'\d', text)) > 3:
            print(f"SPAM DETECTED: Random number/letter mix")
            return True

        # Pattern 3: Repeated character patterns (e.g., asdasdasd, qweqweqwe)
        # Check for 2-3+ character sequences repeated
        # For short text, check 2-char patterns
        min_pattern_len = 2 if len(text) < 10 else 3
        for i in range(min_pattern_len, min(10, len(text) // 2)):
            pattern = text[:i]
            # For very short patterns (2-3 chars), need 3+ repetitions
            # For longer patterns (4+ chars), 2 repetitions is enough
            required_reps = 3 if i <= 3 else 2
            if text.count(pattern) >= required_reps:
                print(f"SPAM DETECTED: Repeated pattern '{pattern}' ({text.count(pattern)} times)")
                return True

        # Pattern 4: Very low vowel ratio
        if len(clean_text) >= 5:
            vowel_ratio = vowel_count / len(clean_text) if len(clean_text) > 0 else 0
            # For short text (5-8 chars), vowel ratio < 20% is suspicious
            # For longer text (8+ chars), vowel ratio < 15% is suspicious
            threshold = 0.20 if len(clean_text) < 8 else 0.15
            if vowel_ratio < threshold:
                print(f"SPAM DETECTED: Very low vowel ratio ({vowel_ratio:.2f}, threshold={threshold})")
                return True

        # Pattern 5: Random keyboard sequences
        keyboard_sequences = ['qwerty', 'asdfgh', 'zxcvbn', 'qaz', 'wsx', 'edc', 'asd', 'jkl']
        text_lower = text.lower()
        for seq in keyboard_sequences:
            if seq in text_lower and len(text_lower) < 15:
                print(f"SPAM DETECTED: Keyboard sequence '{seq}'")
                return True

        # Pattern 6: No recognizable words pattern
        # If text is 5-12 chars and looks completely random (alternating consonants/vowels weirdly)
        if 5 <= len(clean_text) <= 12:
            # Check if it's just random chars with no structure
            # e.g., "asdajd", "qweklm", "hjkasd"
            # Calculate "randomness score"
            char_pairs = [(clean_text[i], clean_text[i+1]) for i in range(len(clean_text)-1)]

            # Count how many times consonants are followed by consonants
            cc_count = 0  # consonant-consonant
            vv_count = 0  # vowel-vowel
            for c1, c2 in char_pairs:
                is_c1_vowel = c1.lower() in vowels
                is_c2_vowel = c2.lower() in vowels
                if not is_c1_vowel and not is_c2_vowel:
                    cc_count += 1
                elif is_c1_vowel and is_c2_vowel:
                    vv_count += 1

            print(f"[SPAM CHECK Pattern 6] clean_text='{clean_text}', len={len(clean_text)}, cc_count={cc_count}, check: {cc_count >= 2 and len(clean_text) <= 8}")

            # If too many consonant clusters OR if pattern looks too random
            # "asdajd" = asd-ajd (2 consonant clusters)
            if cc_count >= 2 and len(clean_text) <= 8:
                print(f"SPAM DETECTED: Multiple consonant clusters in short text ({cc_count} clusters)")
                return True

        return False

    def _fallback_moderate_text(self, text: str) -> Dict:
        """Fallback rule-based moderation"""
        text_lower = text.lower()

        is_toxic = any(keyword in text_lower for keyword in self.toxic_keywords)
        is_spam = self._check_spam(text)
        is_hate_speech = False  # Basic fallback doesn't detect hate speech

        confidence_score = 0.8 if (is_toxic or is_spam) else 0.0

        details = []
        if is_toxic:
            details.append("toxic language detected (rule-based)")
        if is_spam:
            details.append("spam patterns detected")

        return {
            "is_toxic": is_toxic,
            "is_spam": is_spam,
            "is_hate_speech": is_hate_speech,
            "confidence_score": confidence_score,
            "details": ", ".join(details) if details else "content appears safe"
        }

    async def should_block_content(self, moderation_result: Dict) -> bool:
        """
        Determine if content should be blocked based on moderation results
        """
        return (
            moderation_result["is_toxic"] or
            moderation_result["is_spam"] or
            moderation_result["is_hate_speech"]
        )


class ImageModerationService:
    """
    Service for moderating image content (NSFW detection)
    Model: Falconsai/nsfw_image_detection
    """

    def __init__(self):
        try:
            print("=" * 60)
            print("LOADING AI IMAGE MODERATION MODEL...")
            print("=" * 60)
            logger.info("Loading NSFW detection model...")
            from transformers import pipeline

            # Load NSFW detection model
            self.model_name = "Falconsai/nsfw_image_detection"
            print(f"Model: {self.model_name}")
            print("Downloading/Loading image classification model...")

            self.classifier = pipeline(
                "image-classification",
                model=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )

            print("=" * 60)
            print("IMAGE MODERATION MODEL READY!")
            print(f"   - Model: {self.model_name}")
            print(f"   - Type: Image Classification (TRAINED ML MODEL)")
            print(f"   - Purpose: NSFW content detection")
            print("=" * 60)
            logger.info("NSFW detection model loaded successfully!")

            # Load CLIP model for multi-label classification
            print("\n" + "=" * 60)
            print("LOADING CLIP MODEL FOR MULTI-LABEL CLASSIFICATION...")
            print("=" * 60)
            self.clip_model_name = "openai/clip-vit-base-patch32"
            print(f"Model: {self.clip_model_name}")
            print("Loading zero-shot classification model...")

            self.clip_classifier = pipeline(
                "zero-shot-image-classification",
                model=self.clip_model_name,
                device=0 if torch.cuda.is_available() else -1
            )

            print("=" * 60)
            print("CLIP MODEL READY!")
            print(f"   - Model: {self.clip_model_name}")
            print(f"   - Type: Zero-Shot Image Classification")
            print(f"   - Purpose: Violence, gore, scary content detection")
            print("=" * 60)
            logger.info("CLIP model loaded successfully!")
        except Exception as e:
            print(f"ERROR loading image moderation models: {e}")
            logger.error(f"Failed to load image moderation models: {e}")
            logger.warning("Image moderation will default to safe")
            self.classifier = None
            self.clip_classifier = None

    async def moderate_image(self, image_url: str) -> Dict:
        """
        Moderate image for multiple content types:
        - NSFW/Adult content
        - Violence/Weapons/War
        - Gore/Blood
        - Scary/Horror

        Args:
            image_url: URL or base64 encoded image

        Returns:
            Dictionary with moderation results
        """
        print(f"[IMAGE MOD] moderate_image called, URL length: {len(image_url) if image_url else 0}")
        print(f"[IMAGE MOD] Is base64: {image_url.startswith('data:image') if image_url else False}")

        if not self.classifier and not self.clip_classifier:
            # Fallback: assume safe
            print("[IMAGE MOD] No classifiers available, defaulting to safe")
            return {
                "is_nsfw": False,
                "confidence_score": 0.0,
                "passed": True,
                "details": "Image moderation unavailable, defaulting to safe"
            }

        try:
            # Handle base64 images
            if image_url.startswith('data:image'):
                print("[IMAGE MOD] Processing base64 image...")
                import base64
                # Extract base64 data after comma
                image_data = image_url.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                print(f"[IMAGE MOD] Decoded base64, size: {len(image_bytes)} bytes")
            else:
                # Download image from URL
                print(f"[IMAGE MOD] Downloading image from URL...")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image_bytes = response.content
                print(f"[IMAGE MOD] Downloaded, size: {len(image_bytes)} bytes")

            # Open image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            print(f"[IMAGE MOD] Image loaded successfully, size: {image.size}")

            # Initialize scores
            nsfw_score = 0.0
            violence_score = 0.0
            gore_score = 0.0
            scary_score = 0.0

            # 1. NSFW Detection with trained model
            if self.classifier:
                print("\n[IMAGE MODERATION] === NSFW DETECTION ===")
                results = self.classifier(image)

                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    print(f"[IMAGE MODERATION] {label}: {score:.4f}")

                    if 'nsfw' in label:
                        nsfw_score = max(nsfw_score, score)

            # 2. Multi-label classification with CLIP
            if self.clip_classifier:
                print("\n[IMAGE MODERATION] === CLIP MULTI-LABEL CLASSIFICATION ===")

                # Define categories for zero-shot classification
                candidate_labels = [
                    "safe normal content",
                    "violence weapons war military combat",
                    "gore blood graphic injury death",
                    "scary horror disturbing frightening ghost"
                ]

                clip_results = self.clip_classifier(image, candidate_labels=candidate_labels)

                for result in clip_results:
                    label = result['label'].lower()
                    score = result['score']
                    print(f"[IMAGE MODERATION] {label}: {score:.4f}")

                    if 'violence' in label or 'weapon' in label or 'war' in label:
                        violence_score = max(violence_score, score)
                    elif 'gore' in label or 'blood' in label:
                        gore_score = max(gore_score, score)
                    elif 'scary' in label or 'horror' in label:
                        scary_score = max(scary_score, score)

            # Define thresholds
            nsfw_threshold = 0.30     # 30% for NSFW
            violence_threshold = 0.40  # 40% for violence
            gore_threshold = 0.30      # 30% for gore
            scary_threshold = 0.50     # 50% for scary

            # Check if any category exceeds threshold
            is_nsfw = nsfw_score > nsfw_threshold
            is_violence = violence_score > violence_threshold
            is_gore = gore_score > gore_threshold
            is_scary = scary_score > scary_threshold

            # Block if ANY category fails
            passed = not (is_nsfw or is_violence or is_gore or is_scary)

            print(f"\n[IMAGE MODERATION] === FINAL RESULTS ===")
            print(f"[IMAGE MODERATION] NSFW: {nsfw_score:.4f} (threshold: {nsfw_threshold}) - {'BLOCKED' if is_nsfw else 'OK'}")
            print(f"[IMAGE MODERATION] Violence: {violence_score:.4f} (threshold: {violence_threshold}) - {'BLOCKED' if is_violence else 'OK'}")
            print(f"[IMAGE MODERATION] Gore: {gore_score:.4f} (threshold: {gore_threshold}) - {'BLOCKED' if is_gore else 'OK'}")
            print(f"[IMAGE MODERATION] Scary: {scary_score:.4f} (threshold: {scary_threshold}) - {'BLOCKED' if is_scary else 'OK'}")
            print(f"[IMAGE MODERATION] Overall: {'BLOCKED' if not passed else 'PASSED'}")

            # Build detailed message
            blocked_categories = []
            if is_nsfw:
                blocked_categories.append(f"NSFW ({nsfw_score:.2f})")
            if is_violence:
                blocked_categories.append(f"Violence ({violence_score:.2f})")
            if is_gore:
                blocked_categories.append(f"Gore ({gore_score:.2f})")
            if is_scary:
                blocked_categories.append(f"Scary content ({scary_score:.2f})")

            if blocked_categories:
                details = f"Blocked: {', '.join(blocked_categories)}"
            else:
                details = f"Safe content - NSFW: {nsfw_score:.2f}, Violence: {violence_score:.2f}, Gore: {gore_score:.2f}, Scary: {scary_score:.2f}"

            # Return max confidence score of all categories
            max_score = max(nsfw_score, violence_score, gore_score, scary_score)

            return {
                "is_nsfw": is_nsfw or is_violence or is_gore or is_scary,  # True if any category is flagged
                "confidence_score": float(max_score),
                "passed": passed,
                "details": details
            }

        except Exception as e:
            logger.error(f"Image moderation failed: {e}")
            # On error, default to safe to not block legitimate content
            return {
                "is_nsfw": False,
                "confidence_score": 0.0,
                "passed": True,
                "details": f"Moderation failed: {str(e)}, defaulting to safe"
            }


# Singleton instances
content_moderation_service = ContentModerationService()
image_moderation_service = ImageModerationService()
