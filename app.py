import json
from pathlib import Path

try:
    import streamlit as st  # type: ignore[reportMissingImports]
except ModuleNotFoundError:  # pragma: no cover - used when importing for tests
    st = None

APP_DIR = Path(__file__).resolve().parent
API_FILE_PATH = APP_DIR / "apis.json"


def _as_mapping(value):
    return value if isinstance(value, dict) else {}


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class col:
    """Small convenience wrapper around a Streamlit column container."""

    def __init__(self, container):
        self._container = container

    def __getattr__(self, name):
        return getattr(self._container, name)

    def __enter__(self):
        self._container.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._container.__exit__(exc_type, exc_value, traceback)

    def write(self, *args, **kwargs):
        return self._container.write(*args, **kwargs)

    def markdown(self, *args, **kwargs):
        return self._container.markdown(*args, **kwargs)

    def title(self, *args, **kwargs):
        return self._container.title(*args, **kwargs)

    def header(self, *args, **kwargs):
        return self._container.header(*args, **kwargs)

    def subheader(self, *args, **kwargs):
        return self._container.subheader(*args, **kwargs)

    def caption(self, *args, **kwargs):
        return self._container.caption(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._container.info(*args, **kwargs)

    def success(self, *args, **kwargs):
        return self._container.success(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._container.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._container.error(*args, **kwargs)

    def json(self, *args, **kwargs):
        return self._container.json(*args, **kwargs)

    def metric(self, *args, **kwargs):
        return self._container.metric(*args, **kwargs)

    def image(self, *args, **kwargs):
        return self._container.image(*args, **kwargs)

    def button(self, *args, **kwargs):
        return self._container.button(*args, **kwargs)

    def checkbox(self, *args, **kwargs):
        return self._container.checkbox(*args, **kwargs)

    def selectbox(self, *args, **kwargs):
        return self._container.selectbox(*args, **kwargs)

    def multiselect(self, *args, **kwargs):
        return self._container.multiselect(*args, **kwargs)

    def slider(self, *args, **kwargs):
        return self._container.slider(*args, **kwargs)

    def text_input(self, *args, **kwargs):
        return self._container.text_input(*args, **kwargs)

    def number_input(self, *args, **kwargs):
        return self._container.number_input(*args, **kwargs)

    def radio(self, *args, **kwargs):
        return self._container.radio(*args, **kwargs)


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

    data = _as_mapping(load_api_data())

    if not data:
        st.error(
            "⚠️ تنبيه: لم يتم العثور على ملف apis.json. تأكد من وضعه في نفس المجلد مع هذا السكربت."
        )
        return

    image_url = data.get("image")
    if image_url:
        st.sidebar.image(image_url, width=100)
    st.sidebar.title("إدارة نظام Navis")
    st.sidebar.markdown(f"*الإصدار:* {data.get('specificationVersion', 'غير محدد')}")

    delivery_model = _as_mapping(data.get("deliveryModel"))
    st.sidebar.markdown(f"*نموذج الخدمة:* {delivery_model.get('label', 'غير محدد')}")

    menu = st.sidebar.radio(
        "اختر القسم:",
        ["نظرة عامة (Overview)", "واجهات الـ APIs", "الموارد المشتركة والروابط", "عرض ملف JSON الخام"],
    )

    if menu == "نظرة عامة (Overview)":
        st.title(f"🚢 {data.get('name', 'Navis API Management Suite')}")
        st.write(data.get('description', ''))

        apis = _as_list(data.get("apis"))
        access_model = _as_mapping(data.get("accessModel"))
        pricing = access_model.get("pricing", "")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد واجهات الـ APIs", len(apis))
        with col2:
            st.metric("نموذج الوصول", pricing.capitalize() if isinstance(pricing, str) and pricing else "غير محدد")
        with col3:
            st.metric("نوع النشر", str(delivery_model.get("model", "")).upper() or "غير محدد")

        st.subheader("التصنيفات والوسوم:")
        tags = _as_list(data.get("tags"))
        st.write(" ".join(str(tag) for tag in tags))

        st.subheader("فريق الصيانة:")
        for maintainer in _as_list(data.get("maintainers")):
            maintainer_map = _as_mapping(maintainer)
            st.info(f"👤 *{maintainer_map.get('FN', 'غير محدد')}* — البريد الإلكتروني: {maintainer_map.get('email', 'غير محدد')}")

    elif menu == "واجهات الـ APIs":
        st.title("🛠️ واجهات برمجة التطبيقات (APIs)")
        st.markdown("استعراض تفصيلي لجميع نقاط النهاية والمسارات الخاصة بنظام إدارة الموانئ:")

        apis = [api for api in _as_list(data.get("apis")) if isinstance(api, dict)]
        if not apis:
            st.warning("لا توجد واجهات API في الملف الحالي.")
            return

        api_names = [api.get("name", "بدون اسم") for api in apis]
        api_selection = st.selectbox("اختر واجهة API للاستعراض:", api_names)
        selected_api = next((api for api in apis if api.get("name") == api_selection), apis[0])

        st.subheader(selected_api.get("name", "واجهة API"))
        st.write(f"*الوصف:* {selected_api.get('description', '')}")
        st.write(f"*المعرف (AID):* {selected_api.get('aid', 'غير محدد')}")
        human_url = selected_api.get("humanURL")
        if human_url:
            st.write(f"*الرابط البشري:* [زيارة الموقع الرسمي]({human_url})")

        st.markdown("### 📂 خصائص وملفات الـ API المرتبطة:")
        for prop in _as_list(selected_api.get("properties")):
            prop_map = _as_mapping(prop)
            st.markdown(f"- *{prop_map.get('type', 'غير محدد')}:* {prop_map.get('url', '')}")

    elif menu == "الموارد المشتركة والروابط":
        st.title("🔗 الموارد المشتركة وروابط النظام")
        st.markdown("قائمة بالملفات التنظيمية، سياسات الأمان، وصفحات الدعم الملحقة:")

        cols = [col(container) for container in st.columns(2)]
        for idx, item in enumerate(_as_list(data.get("common"))):
            column = cols[idx % 2]
            with column:
                item_map = _as_mapping(item)
                item_type = item_map.get("type", "مورد")
                item_url = item_map.get("url", "")
                column.markdown(f"🔹 *{item_type}*: [{item_url}]({item_url})")

    elif menu == "عرض ملف JSON الخام":
        st.title("📄 محتوى ملف الفهرس (JSON)")
        st.markdown("يمكنك معاينة هيكل البيانات الكامل الخاص بالمشروع هنا:")
        st.json(data)


if __name__ == "__main__":
    main()
