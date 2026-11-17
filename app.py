import json
from pathlib import Path

try:
    import streamlit as st  # type: ignore[reportMissingImports]
except ModuleNotFoundError:  # pragma: no cover - used when importing for tests
    st = None

APP_DIR = Path(__file__).resolve().parent
API_FILE_PATH = APP_DIR / "apis.json"


def _cache_data_decorator():
    if st is None:
        def decorator(func):
            return func
        return decorator
    return st.cache_data


@_cache_data_decorator()
def load_api_data():
    try:
        with API_FILE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main():
    if st is None:
        raise RuntimeError("Streamlit is required to run this app. Install it with 'pip install streamlit'.")

    st.set_page_config(
        page_title="Navis API Management Suite",
        page_icon="🚢",
        layout="wide",
    )

    data = load_api_data()

    if data is None:
        st.error(
            "⚠️ تنبيه: لم يتم العثور على ملف apis.json. تأكد من وضعه في نفس المجلد مع هذا السكربت."
        )
        return

    image_url = data.get("image")
    if image_url:
        st.sidebar.image(image_url, width=100)
    st.sidebar.title("إدارة نظام Navis")
    st.sidebar.markdown(f"*الإصدار:* {data.get('specificationVersion', 'غير محدد')}")

    delivery_model = data.get("deliveryModel") or {}
    st.sidebar.markdown(f"*نموذج الخدمة:* {delivery_model.get('label', 'غير محدد')}")

    menu = st.sidebar.radio(
        "اختر القسم:",
        ["نظرة عامة (Overview)", "واجهات الـ APIs", "الموارد المشتركة والروابط", "عرض ملف JSON الخام"],
    )

    if menu == "نظرة عامة (Overview)":
        st.title(f"🚢 {data.get('name', 'Navis API Management Suite')}")
        st.write(data.get('description', ''))

        apis = data.get("apis", [])
        access_model = data.get("accessModel") or {}
        pricing = access_model.get("pricing", "")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد واجهات الـ APIs", len(apis))
        with col2:
            st.metric("نموذج الوصول", pricing.capitalize() if pricing else "غير محدد")
        with col3:
            st.metric("نوع النشر", str(delivery_model.get("model", "")).upper() or "غير محدد")

        st.subheader("التصنيفات والوسوم:")
        tags = data.get("tags", [])
        st.write(" ".join(str(tag) for tag in tags))

        st.subheader("فريق الصيانة:")
        for maintainer in data.get("maintainers", []):
            st.info(f"👤 *{maintainer.get('FN', 'غير محدد')}* — البريد الإلكتروني: {maintainer.get('email', 'غير محدد')}")

    elif menu == "واجهات الـ APIs":
        st.title("🛠️ واجهات برمجة التطبيقات (APIs)")
        st.markdown("استعراض تفصيلي لجميع نقاط النهاية والمسارات الخاصة بنظام إدارة الموانئ:")

        apis = data.get("apis", [])
        if not apis:
            st.warning("لا توجد واجهات API في الملف الحالي.")
            return

        api_selection = st.selectbox(
            "اختر واجهة API للاستعراض:",
            [api.get("name", "بدون اسم") for api in apis],
        )
        selected_api = next(api for api in apis if api.get("name") == api_selection)

        st.subheader(selected_api.get("name", "واجهة API"))
        st.write(f"*الوصف:* {selected_api.get('description', '')}")
        st.write(f"*المعرف (AID):* {selected_api.get('aid', 'غير محدد')}")
        human_url = selected_api.get("humanURL")
        if human_url:
            st.write(f"*الرابط البشري:* [زيارة الموقع الرسمي]({human_url})")

        st.markdown("### 📂 خصائص وملفات الـ API المرتبطة:")
        for prop in selected_api.get("properties", []):
            st.markdown(f"- *{prop.get('type', 'غير محدد')}:* {prop.get('url', '')}")

    elif menu == "الموارد المشتركة والروابط":
        st.title("🔗 الموارد المشتركة وروابط النظام")
        st.markdown("قائمة بالملفات التنظيمية، سياسات الأمان، وصفحات الدعم الملحقة:")

        cols = st.columns(2)
        for idx, item in enumerate(data.get("common", [])):
            col = cols[idx % 2]
            with col:
                item_type = item.get("type", "مورد")
                item_url = item.get("url", "")
                st.markdown(f"🔹 *{item_type}*: [{item_url}]({item_url})")

    elif menu == "عرض ملف JSON الخام":
        st.title("📄 محتوى ملف الفهرس (JSON)")
        st.markdown("يمكنك معاينة هيكل البيانات الكامل الخاص بالمشروع هنا:")
        st.json(data)


if __name__ == "__main__":
    main()
