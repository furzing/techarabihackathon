from groq import Groq
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class Groq_Env:
    def __init__(self, API_Key=None, Model="qwen/qwen3-32b"):
        """
        Initialize the Groq_Env class with the API key and model name.
        """
        if API_Key is None:
            API_Key = os.getenv("GROQ_api_key")
        
        if not API_Key:
            raise ValueError("GROQ API key not found. Please set GROQ_api_key in your environment.")
        
        self.act = """أنت خبير في إدارة وسائل التواصل الاجتماعي والتسويق الرقمي. مهمتك هي تقديم استراتيجيات تسويقية فعالة ومحتوى جذاب للشركات والأعمال في المنطقة العربية. 

يجب أن تراعي:
- الثقافة العربية والقيم المحلية
- أفضل الممارسات في التسويق الرقمي
- الاتجاهات الحديثة في وسائل التواصل الاجتماعي
- تقديم إجابات عملية وقابلة للتطبيق
- الإجابة باللغة العربية بأسلوب مهني وواضح"""
        
        self._client = Groq(api_key=API_Key)
        self.model = Model

    def Groq_chat_answer(self, role="user", messages_content="",
                         temperature=0.7, max_completion_tokens=2000, top_p=0.9):
        """
        Generate an AI response as a string with enhanced error handling.
        """
        try:
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.act},
                    {"role": role, "content": messages_content}
                ],
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
                top_p=top_p,
                stream=True
            )

            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content
            
            return answer.strip()
        
        except Exception as e:
            logging.error(f"Error in Groq API call: {str(e)}")
            raise Exception(f"فشل في الحصول على استجابة من الذكاء الاصطناعي: {str(e)}")


class SocialMediaManager:
    def __init__(self, groq_env: Groq_Env):
        self.groq = groq_env

    def generate_strategy(self, business_info):
        prompt = f"""
        قم بإنشاء استراتيجية تسويق شاملة لوسائل التواصل الاجتماعي لهذا العمل:

        **معلومات العمل:**
        - اسم العمل: {business_info.business_name}
        - نوع العمل: {business_info.business_type}
        - الجمهور المستهدف: {business_info.target_audience}
        - الموقع: {business_info.location}
        - نقاط القوة الفريدة: {business_info.unique_selling_points or "غير محدد"}

        **يجب أن تشمل الاستراتيجية:**
        1. تحليل الجمهور المستهدف التفصيلي
        2. الهوية البصرية ونبرة الصوت المناسبة
        3. المنصات الأنسب للاستخدام مع التبرير
        4. أعمدة المحتوى الرئيسية (Content Pillars)
        5. الأهداف القابلة للقياس
        6. استراتيجية التفاعل مع الجمهور
        7. التحديات المتوقعة وكيفية التعامل معها

        قدم الاستراتيجية بشكل منظم ومفصل وعملي.
        """
        return self.groq.Groq_chat_answer(messages_content=prompt)

    def create_marketing_plan(self, strategy, duration="1 month"):
        prompt = f"""
        بناءً على هذه الاستراتيجية:
        {strategy}

        قم بإنشاء خطة تسويقية مفصلة لمدة {duration} تشمل:

        **الخطة يجب أن تحتوي على:**
        1. جدولة زمنية أسبوعية مع المواضيع الرئيسية
        2. أهداف محددة وقابلة للقياس لكل أسبوع
        3. مؤشرات الأداء الرئيسية (KPIs) المناسبة
        4. أنواع المحتوى المقترح لكل يوم
        5. أوقات النشر المثلى
        6. الميزانية المقترحة إذا كانت مطلوبة
        7. استراتيجية الهاشتاغات
        8. خطة للتفاعل مع التعليقات والرسائل

        اجعل الخطة عملية وقابلة للتطبيق مباشرة.
        """
        return self.groq.Groq_chat_answer(messages_content=prompt)

    def suggest_content(self, topic, content_type="all", target_platform="Instagram"):
        prompt = f"""
        اقترح أفكار محتوى جذابة ومبتكرة حول موضوع "{topic}" لمنصة {target_platform}.

        **متطلبات المحتوى:**
        - نوع المحتوى المطلوب: {content_type}
        - يجب أن يكون المحتوى مناسب للثقافة العربية
        - قابل للتطبيق والتنفيذ
        - يحفز على التفاعل والمشاركة

        **اقترح على الأقل 10 أفكار متنوعة تشمل:**
        1. منشورات نصية تفاعلية
        2. أفكار للصور مع أوصاف مفصلة
        3. مقاطع فيديو قصيرة
        4. قصص (Stories) تفاعلية
        5. استطلاعات وأسئلة للجمهور
        6. محتوى تعليمي
        7. محتوى ترفيهي
        8. محتوى وراء الكواليس
        9. تحديات ومسابقات
        10. شهادات العملاء

        لكل فكرة، اذكر:
        - العنوان المقترح
        - وصف المحتوى
        - الهدف من المنشور
        - الهاشتاغات المناسبة
        """
        return self.groq.Groq_chat_answer(messages_content=prompt)

    def create_post(self, idea, platform="Instagram", tone="engaging"):
        prompt = f"""
        قم بإنشاء منشور جاهز للنشر على منصة {platform} بناءً على هذه الفكرة:
        "{idea}"

        **مواصفات المنشور:**
        - النبرة المطلوبة: {tone}
        - مناسب للثقافة العربية
        - يحفز على التفاعل والمشاركة

        **يجب أن يشمل المنشور:**
        1. **النص الرئيسي:** نص جذاب ومناسب لطول المنصة
        2. **دعوة للعمل (CTA):** واضحة ومحفزة
        3. **الهاشتاغات:** 15-20 هاشتاغ مناسب ومتنوع
        4. **وصف الصورة/الفيديو المقترح:** وصف مفصل للمحتوى البصري
        5. **أفضل وقت للنشر:** اقترح التوقيت الأمثل
        6. **استراتيجية التفاعل:** كيفية الرد على التعليقات المتوقعة

        اجعل المنشور احترافي وجذاب ومناسب للهدف المحدد.
        """
        return self.groq.Groq_chat_answer(messages_content=prompt)

    def moderate_post(self, post_content):
        prompt = f"""
        قم بتحليل هذا المنشور للتأكد من مطابقته لمعايير النشر وسياسات المنصات:

        **المحتوى المراد تحليله:**
        {post_content}

        **نقاط التحليل المطلوبة:**
        1. **فحص خطاب الكراهية:** هل يحتوي على أي محتوى يحرض على الكراهية؟
        2. **انتهاك حقوق الطبع والنشر:** هل يحتوي على محتوى محمي بحقوق النشر؟
        3. **مخالفة إرشادات المجتمع:** هل يخالف قواعد المنصات الاجتماعية؟
        4. **المحتوى المضلل:** هل يحتوي على معلومات خاطئة أو مضللة؟
        5. **الملاءمة الثقافية:** هل مناسب للثقافة العربية والقيم المحلية؟
        6. **جودة اللغة:** فحص القواعد النحوية والإملائية

        **النتيجة يجب أن تشمل:**
        - تقييم عام (آمن/يحتاج تعديل/غير مناسب)
        - قائمة بالمشاكل المكتشفة إن وجدت
        - اقتراحات للتحسين
        - درجة الأمان من 1-10
        - توصيات قبل النشر

        كن دقيقاً ومفصلاً في التحليل.
        """
        return self.groq.Groq_chat_answer(messages_content=prompt)