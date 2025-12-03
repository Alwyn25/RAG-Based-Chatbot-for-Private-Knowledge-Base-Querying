"""
Test Data Loader for Customer Support Chatbot System
Creates sample conversation data for testing and demonstration purposes.
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestDataLoader:
    def __init__(self):
        """Initialize MongoDB connection"""
        MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client.customer_support
        self.chat_logs = self.db.chat_logs
        self.support_queue = self.db.support_queue
        self.docs_indexed = self.db.docs_indexed
        
        # Sample data templates
        self.categories = ["Product FAQ", "Tech issue", "Transactional"]
        self.languages = ["en", "ar"]
        self.feedback_types = ["like", "dislike", None]
        
        # Sample conversations in English
        self.sample_conversations_en = [
            {
                "user_message": "How do I reset my password?",
                "bot_response": "To reset your password, please follow these steps: 1) Go to the login page, 2) Click 'Forgot Password', 3) Enter your email address, 4) Check your email for reset instructions. If you need further assistance, please contact our support team.",
                "category": "Tech issue",
                "confidence": 0.85
            },
            {
                "user_message": "What are your business hours?",
                "bot_response": "Our customer service is available Monday to Friday from 9:00 AM to 6:00 PM (EST). For urgent technical issues, we offer 24/7 support through our emergency hotline.",
                "category": "Product FAQ",
                "confidence": 0.92
            },
            {
                "user_message": "I want to cancel my subscription",
                "bot_response": "I understand you'd like to cancel your subscription. You can do this by going to your account settings and selecting 'Cancel Subscription'. Please note that cancellation will take effect at the end of your current billing cycle. Would you like me to guide you through the process?",
                "category": "Transactional",
                "confidence": 0.78
            },
            {
                "user_message": "The app keeps crashing on my phone",
                "bot_response": "I'm sorry to hear about the app crashes. Let's troubleshoot this issue: 1) Try force-closing and reopening the app, 2) Restart your device, 3) Check if you have the latest app version, 4) Clear the app cache. If the problem persists, please provide your device model and OS version for further assistance.",
                "category": "Tech issue",
                "confidence": 0.88
            },
            {
                "user_message": "Do you offer student discounts?",
                "bot_response": "Yes! We offer a 20% student discount on all our plans. To qualify, you'll need to verify your student status through our partner verification service. You can apply for the discount in your account settings under 'Student Discount'.",
                "category": "Product FAQ",
                "confidence": 0.95
            },
            {
                "user_message": "My last payment was charged twice",
                "bot_response": "I apologize for the billing issue. Double charges can occur due to processing delays. Please check if one charge is pending and will be reversed automatically within 3-5 business days. If both charges are completed, please contact our billing department with your transaction details for immediate assistance.",
                "category": "Transactional",
                "confidence": 0.72
            },
            {
                "user_message": "How can I upgrade my account?",
                "bot_response": "You can upgrade your account anytime by visiting the 'Billing' section in your account settings. Choose your desired plan and follow the payment process. Your upgrade will be active immediately, and you'll be billed pro-rata for the remaining period.",
                "category": "Transactional",
                "confidence": 0.90
            },
            {
                "user_message": "Is my data secure with your service?",
                "bot_response": "Absolutely! We take data security very seriously. Your data is encrypted both in transit and at rest using industry-standard AES-256 encryption. We're also SOC 2 Type II certified and comply with GDPR regulations. You can read more about our security measures in our Privacy Policy.",
                "category": "Product FAQ",
                "confidence": 0.93
            }
        ]
        
        # Sample conversations in Arabic
        self.sample_conversations_ar = [
            {
                "user_message": "كيف يمكنني إعادة تعيين كلمة المرور؟",
                "bot_response": "لإعادة تعيين كلمة المرور، يرجى اتباع هذه الخطوات: 1) اذهب إلى صفحة تسجيل الدخول، 2) انقر على 'نسيت كلمة المرور'، 3) أدخل عنوان بريدك الإلكتروني، 4) تحقق من بريدك الإلكتروني للحصول على تعليمات إعادة التعيين. إذا كنت بحاجة إلى مساعدة إضافية، يرجى الاتصال بفريق الدعم.",
                "category": "Tech issue",
                "confidence": 0.82
            },
            {
                "user_message": "ما هي ساعات العمل؟",
                "bot_response": "خدمة العملاء متاحة من الاثنين إلى الجمعة من الساعة 9:00 صباحاً حتى 6:00 مساءً (بتوقيت شرق الولايات المتحدة). للقضايا التقنية العاجلة، نقدم دعماً على مدار 24 ساعة طوال أيام الأسبوع من خلال خط الطوارئ.",
                "category": "Product FAQ",
                "confidence": 0.89
            },
            {
                "user_message": "أريد إلغاء اشتراكي",
                "bot_response": "أفهم أنك تريد إلغاء اشتراكك. يمكنك القيام بذلك من خلال الذهاب إلى إعدادات حسابك واختيار 'إلغاء الاشتراك'. يرجى ملاحظة أن الإلغاء سيسري في نهاية دورة الفوترة الحالية. هل تريد مني أن أوجهك خلال العملية؟",
                "category": "Transactional",
                "confidence": 0.75
            },
            {
                "user_message": "التطبيق يتعطل باستمرار على هاتفي",
                "bot_response": "أعتذر لسماع عن تعطل التطبيق. دعنا نحل هذه المشكلة: 1) حاول إغلاق التطبيق بالقوة وإعادة فتحه، 2) أعد تشغيل جهازك، 3) تحقق من وجود أحدث إصدار من التطبيق، 4) امسح ذاكرة التخزين المؤقت للتطبيق. إذا استمرت المشكلة، يرجى تقديم طراز جهازك وإصدار نظام التشغيل للمساعدة الإضافية.",
                "category": "Tech issue",
                "confidence": 0.84
            }
        ]
        
        # Sample feedback comments
        self.feedback_comments = [
            "Very helpful, solved my problem quickly",
            "The response was accurate and detailed",
            "Could be more specific about the steps",
            "Didn't fully address my concern",
            "Great customer service!",
            "Response was too generic",
            "Perfect, exactly what I needed",
            "Could use more examples",
            "التوضيح كان ممتازاً",
            "أحتاج المزيد من التفاصيل",
            "الرد كان سريعاً ومفيداً",
            "لم يحل مشكلتي تماماً"
        ]

    def generate_user_id(self) -> str:
        """Generate a realistic user ID"""
        prefixes = ["user", "customer", "guest", "anon"]
        suffix = random.randint(1000, 9999)
        return f"{random.choice(prefixes)}_{suffix}"

    def generate_session_id(self) -> str:
        """Generate a session ID"""
        timestamp = int(datetime.now().timestamp())
        random_suffix = random.randint(100, 999)
        return f"session_{timestamp}_{random_suffix}"

    def generate_timestamp(self, days_back: int = 30) -> datetime:
        """Generate a random timestamp within the last N days"""
        now = datetime.utcnow()
        start_date = now - timedelta(days=days_back)
        random_seconds = random.randint(0, int((now - start_date).total_seconds()))
        return start_date + timedelta(seconds=random_seconds)

    def create_chat_log(self, conversation: Dict[str, Any], language: str, user_id: str, session_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Create a chat log entry"""
        # Determine if resolved based on confidence
        resolved = conversation["confidence"] > 0.6
        
        # Random feedback
        feedback_type = random.choice(self.feedback_types) if random.random() > 0.3 else None
        feedback_comment = random.choice(self.feedback_comments) if feedback_type and random.random() > 0.5 else None
        
        chat_log = {
            "user_id": user_id,
            "session_id": session_id,
            "message": conversation["user_message"],
            "response": conversation["bot_response"],
            "language": language,
            "category": conversation["category"],
            "confidence": conversation["confidence"],
            "timestamp": timestamp,
            "resolved": resolved,
            "feedback_type": feedback_type,
            "feedback_comment": feedback_comment
        }
        
        if feedback_type:
            chat_log["feedback_timestamp"] = timestamp + timedelta(minutes=random.randint(1, 30))
        
        return chat_log

    def create_support_queue_item(self, chat_log: Dict[str, Any]) -> Dict[str, Any]:
        """Create a support queue item for unresolved chats"""
        return {
            "chat_id": str(chat_log.get("_id", "unknown")),
            "user_id": chat_log["user_id"],
            "session_id": chat_log["session_id"],
            "message": chat_log["message"],
            "response": chat_log["response"],
            "category": chat_log["category"],
            "confidence": chat_log["confidence"],
            "feedback_comment": chat_log.get("feedback_comment"),
            "timestamp": chat_log["timestamp"],
            "status": random.choice(["pending", "in_progress", "escalated"])
        }

    def create_document_metadata(self) -> List[Dict[str, Any]]:
        """Create sample document metadata"""
        sample_docs = [
            {
                "filename": "user_manual.pdf",
                "file_path": "input/user_manual.pdf",
                "file_hash": "abc123def456",
                "file_type": ".pdf",
                "file_size": 2048576,
                "chunk_count": 45,
                "indexed_at": datetime.utcnow() - timedelta(days=5),
                "status": "indexed"
            },
            {
                "filename": "faq_document.docx",
                "file_path": "input/faq_document.docx",
                "file_hash": "def456ghi789",
                "file_type": ".docx",
                "file_size": 1024000,
                "chunk_count": 28,
                "indexed_at": datetime.utcnow() - timedelta(days=3),
                "status": "indexed"
            },
            {
                "filename": "product_specifications.html",
                "file_path": "input/product_specifications.html",
                "file_hash": "ghi789jkl012",
                "file_type": ".html",
                "file_size": 512000,
                "chunk_count": 15,
                "indexed_at": datetime.utcnow() - timedelta(days=2),
                "status": "indexed"
            },
            {
                "filename": "troubleshooting_guide.md",
                "file_path": "input/troubleshooting_guide.md",
                "file_hash": "jkl012mno345",
                "file_type": ".md",
                "file_size": 256000,
                "chunk_count": 22,
                "indexed_at": datetime.utcnow() - timedelta(days=1),
                "status": "indexed"
            }
        ]
        return sample_docs

    def clear_existing_data(self):
        """Clear existing test data"""
        print("Clearing existing test data...")
        self.chat_logs.delete_many({})
        self.support_queue.delete_many({})
        self.docs_indexed.delete_many({})
        print("Existing data cleared.")

    def load_test_data(self, num_conversations: int = 100, clear_existing: bool = True):
        """Load test data into MongoDB"""
        if clear_existing:
            self.clear_existing_data()
        
        print(f"Loading {num_conversations} test conversations...")
        
        # Generate chat logs
        chat_logs_to_insert = []
        support_queue_items = []
        
        for i in range(num_conversations):
            # Choose language (70% English, 30% Arabic)
            language = "en" if random.random() > 0.3 else "ar"
            
            # Choose conversation based on language
            conversations = self.sample_conversations_en if language == "en" else self.sample_conversations_ar
            conversation = random.choice(conversations)
            
            # Generate unique identifiers
            user_id = self.generate_user_id()
            session_id = self.generate_session_id()
            timestamp = self.generate_timestamp()
            
            # Create chat log
            chat_log = self.create_chat_log(conversation, language, user_id, session_id, timestamp)
            chat_logs_to_insert.append(chat_log)
            
            # Add to support queue if unresolved or negative feedback
            if not chat_log["resolved"] or chat_log.get("feedback_type") == "dislike":
                support_queue_items.append(self.create_support_queue_item(chat_log))
        
        # Insert chat logs
        if chat_logs_to_insert:
            result = self.chat_logs.insert_many(chat_logs_to_insert)
            print(f"Inserted {len(result.inserted_ids)} chat logs")
            
            # Update support queue items with actual chat IDs
            for i, item in enumerate(support_queue_items):
                if i < len(result.inserted_ids):
                    item["chat_id"] = str(result.inserted_ids[i])
        
        # Insert support queue items
        if support_queue_items:
            result = self.support_queue.insert_many(support_queue_items)
            print(f"Inserted {len(result.inserted_ids)} support queue items")
        
        # Insert document metadata
        doc_metadata = self.create_document_metadata()
        if doc_metadata:
            result = self.docs_indexed.insert_many(doc_metadata)
            print(f"Inserted {len(result.inserted_ids)} document metadata records")
        
        print("Test data loading completed!")

    def generate_additional_conversations(self, num_today: int = 20):
        """Generate additional conversations for today to simulate real-time activity"""
        print(f"Generating {num_today} conversations for today...")
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        chat_logs_to_insert = []
        support_queue_items = []
        
        for i in range(num_today):
            language = "en" if random.random() > 0.3 else "ar"
            conversations = self.sample_conversations_en if language == "en" else self.sample_conversations_ar
            conversation = random.choice(conversations)
            
            user_id = self.generate_user_id()
            session_id = self.generate_session_id()
            
            # Generate timestamp for today
            seconds_today = random.randint(0, int((datetime.utcnow() - today_start).total_seconds()))
            timestamp = today_start + timedelta(seconds=seconds_today)
            
            chat_log = self.create_chat_log(conversation, language, user_id, session_id, timestamp)
            chat_logs_to_insert.append(chat_log)
            
            if not chat_log["resolved"] or chat_log.get("feedback_type") == "dislike":
                support_queue_items.append(self.create_support_queue_item(chat_log))
        
        # Insert today's conversations
        if chat_logs_to_insert:
            result = self.chat_logs.insert_many(chat_logs_to_insert)
            print(f"Inserted {len(result.inserted_ids)} conversations for today")
            
            # Update support queue items with actual chat IDs
            for i, item in enumerate(support_queue_items):
                if i < len(result.inserted_ids):
                    item["chat_id"] = str(result.inserted_ids[i])
        
        if support_queue_items:
            result = self.support_queue.insert_many(support_queue_items)
            print(f"Added {len(result.inserted_ids)} items to support queue")

    def print_summary(self):
        """Print a summary of the test data"""
        total_chats = self.chat_logs.count_documents({})
        resolved_chats = self.chat_logs.count_documents({"resolved": True})
        unresolved_chats = total_chats - resolved_chats
        support_queue_count = self.support_queue.count_documents({})
        docs_count = self.docs_indexed.count_documents({})
        
        # Language distribution
        en_chats = self.chat_logs.count_documents({"language": "en"})
        ar_chats = self.chat_logs.count_documents({"language": "ar"})
        
        # Category distribution
        categories = self.chat_logs.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        # Feedback distribution
        positive_feedback = self.chat_logs.count_documents({"feedback_type": "like"})
        negative_feedback = self.chat_logs.count_documents({"feedback_type": "dislike"})
        
        print("\n" + "="*50)
        print("TEST DATA SUMMARY")
        print("="*50)
        print(f"Total Chats: {total_chats}")
        print(f"Resolved: {resolved_chats} ({resolved_chats/total_chats*100:.1f}%)")
        print(f"Unresolved: {unresolved_chats} ({unresolved_chats/total_chats*100:.1f}%)")
        print(f"Support Queue Items: {support_queue_count}")
        print(f"Indexed Documents: {docs_count}")
        print()
        print("Language Distribution:")
        print(f"  English: {en_chats} ({en_chats/total_chats*100:.1f}%)")
        print(f"  Arabic: {ar_chats} ({ar_chats/total_chats*100:.1f}%)")
        print()
        print("Category Distribution:")
        for cat in categories:
            percentage = cat["count"] / total_chats * 100
            print(f"  {cat['_id']}: {cat['count']} ({percentage:.1f}%)")
        print()
        print("Feedback Distribution:")
        print(f"  Positive: {positive_feedback}")
        print(f"  Negative: {negative_feedback}")
        print(f"  No Feedback: {total_chats - positive_feedback - negative_feedback}")
        print("="*50)


def main():
    """Main function to run the test data loader"""
    print("Customer Support Chatbot - Test Data Loader")
    print("=" * 50)
    
    loader = TestDataLoader()
    
    try:
        # Load main test data
        loader.load_test_data(num_conversations=150, clear_existing=True)
        
        # Generate additional conversations for today
        loader.generate_additional_conversations(num_today=25)
        
        # Print summary
        loader.print_summary()
        
        print("\nTest data has been successfully loaded!")
        print("You can now:")
        print("1. Start the chatbot service: python chatbot_service/main.py")
        print("2. Start the dashboard service: python dashboard_service/main.py")
        print("3. View the dashboard at http://localhost:5000")
        print("4. Test the chat widget by opening chat_widget/chat_widget.html")
        
    except Exception as e:
        print(f"Error loading test data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        loader.client.close()


if __name__ == "__main__":
    main()
