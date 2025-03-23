# system_prompts.py
# This script defines system prompts in multiple languages for use in an
# AI-driven assistant.
# The prompts are structured to guide interactions between a human user and
# the AI.
# An enumeration `Language` is used to define the supported languages in a
# structured way.

from enum import Enum


# Enumeration to define supported languages
class Language(Enum):
    ENGLISH = "en"  # English language code
    FRENCH_CA = "fr-ca"  # Canadian French language code
    # Add other languages here if needed


# Set default language (English)
locale = Language.ENGLISH.value  # Default language is set to English

# Dictionary containing prompts in different languages
prompts = {
    "en": {
        # Prompt for answering questions using provided context
        "qa_prompt": (
            """Hãy sử dụng các phần ngữ cảnh sau để trả lời câu hỏi ở cuối. Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết - đừng tự suy diễn hay bịa ra. Một số thuật ngữ cần lưu ý:
- 'NVL': Nguyên vật liệu gỗ.
- 'Planned Price 1': Giá dự kiến."""
        ),
        # Prompt for conversational interaction between a human and AI
        "conversation_prompt": (
            """Sau đây là cuộc trò chuyện thân thiện giữa con người và AI. Nếu AI không biết câu trả lời cho một câu hỏi, nó sẽ thành thật nói rằng nó không biết. Một số thuật ngữ cần lưu ý:
- 'NVL': Nguyên vật liệu gỗ.
- 'Planned Price 1': Giá dự kiến."""
        ),
        # Prompt for rephrasing a follow-up question to be a standalone question
        "condense_question_prompt": (
            """Với cuộc trò chuyện sau và một câu hỏi tiếp theo, hãy diễn đạt lại câu hỏi tiếp theo thành một câu hỏi độc lập. Một số thuật ngữ cần lưu ý: 
- 'NVL': Nguyên vật liệu gỗ.
- 'Planned Price 1': Giá dự kiến."""
        ),
        "current_conversation_word": "Current conversation",
        "question_word": "Question",
        "assistant_word": "Assistant",
        "chat_history_word": "Chat History",
        "follow_up_input_word": "Follow Up Input",
        "standalone_question_word": "Standalone question",
        "helpful_answer_word": "Helpful Answer",
    },
    "fr-ca": {
        # Prompt for answering questions using provided context (French-Canadian)
        "qa_prompt": (
            "Vous êtes un assistant IA utilisant la Génération Augmentée par "
            "Récupération (RAG). "
            "Répondez aux questions de l'utilisateur uniquement en vous basant sur "
            "les informations contenues dans les documents fournis. "
            "N'ajoutez aucune information supplémentaire et ne faites aucune "
            "supposition qui ne soit pas directement soutenue par ces documents. "
            "Si vous ne trouvez pas la réponse dans les documents, informez "
            "l'utilisateur que l'information n'est pas disponible. "
            "Si possible, dressez la liste des documents référencés."
        ),
        # Prompt for conversational interaction between a human and AI (French-Canadian)
        "conversation_prompt": (
            "Vous êtes un assistant IA capable de répondre aux questions "
            "en fonction de vos connaissances préalables. "
            "Répondez aux questions de l'utilisateur uniquement avec des informations "
            "que vous connaissez déjà. "
            "N'ajoutez aucune information non vérifiée ou spéculative. "
            "Si vous ne connaissez pas la réponse à une question, informez "
            "l'utilisateur que vous n'avez pas suffisamment d'informations "
            "pour répondre."
        ),
        # Prompt for rephrasing a follow-up question to be a
        # standalone question (French-Canadian)
        "condense_question_prompt": (
            "Avec la conversation ci-dessous et la question de suivi, "
            "reformulez la question de suivi de manière à ce qu'elle soit "
            "une question autonome."
        ),
        "current_conversation_word": "Conversation en cours",
        "question_word": "Question",
        "assistant_word": "Assistant",
        "chat_history_word": "Historique de la discussion",
        "follow_up_input_word": "Question de suivi",
        "standalone_question_word": "Question indépendante",
        "helpful_answer_word": "Réponse utile",
    },
    # Add other languages here if needed
}
