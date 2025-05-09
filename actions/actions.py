import requests
import json
from rasa_sdk import Action, Tracker
from typing import Any, Dict, List, Text
from rasa_sdk.executor import CollectingDispatcher

with open('resources/images_intent.json', "r", encoding="utf-8") as f:
    image_data = json.load(f)


class ActionFinetuneAnswer(Action):

    def name(self):
        return "action_finetune_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get("intent", {}).get("name")

        raw_answer = self._get_raw_answer(domain, intent)
        if not raw_answer:
            dispatcher.utter_message(text="Xin lỗi, tôi chưa có câu trả lời cho câu hỏi này.")
            return []

        improved = self._rewrite_with_gemini(raw_answer)
        # text = improved,
        if intent in image_data:
            dispatcher.utter_message(text=improved)

            images = image_data[intent]
            for img_url in images:
                dispatcher.utter_message(image=img_url)
        else:
            dispatcher.utter_message(text=improved)

        return []

    @staticmethod
    def _get_raw_answer(domain: dict, intent: Text) -> Text:
        key = f"utter_{intent}"
        return domain.get("responses", {}).get(key, [{}])[0].get("text", "")

    @staticmethod
    def _rewrite_with_gemini(text: Text) -> Text:
        api_key = "AIzaSyAAHCF-_2H37wix8KgZprNTLnmS87IIFwk"
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.0-flash:generateContent"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Hãy viết lại đoạn sau bằng tiếng Việt theo phong cách "
                                "thân thiện, dễ hiểu, có cảm xúc, như một người hướng dẫn "
                                f"tận tâm đang giúp người khác hiểu rõ vấn đề:\n\n{text}"
                            )
                        }
                    ]
                }
            ]
        }

        try:
            resp = requests.post(f"{url}?key={api_key}", json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"(Lỗi gọi Gemini: {e})\n\n{text}"
