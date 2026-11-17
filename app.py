import json
import streamlit as st  # type: ignore[reportMissingImports]

# إعدادات وتصميم الصفحة
st.set_page_config(
    page_title="Navis API Management Suite",
    page_icon="🚢",
    layout="wide"
)

# دالة لتحميل ملف apis.json مباشرة
@st.cache_data
def load_api_data():
    try:
        with open('apis.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

data = load_api_data()

if data is None:
    st.error("⚠️ تنبيه: لم يتم العثور على ملف apis.json. تأكد من وضعه في نفس المجلد مع هذا السكربت.")
else:
    # القائمة الجانبية للتنقل بين أقسام التطبيق
    st.sidebar.image(data.get("image"), width=100)
    st.sidebar.title("إدارة نظام Navis")
    st.sidebar.markdown(f"*الإصدار:* {data.get('specificationVersion')}")
    st.sidebar.markdown(f"*نموذج الخدمة:* {data['deliveryModel']['label']}")

    menu = st.sidebar.radio("اختر القسم:", ["نظرة عامة (Overview)", "واجهات الـ APIs", "الموارد المشتركة والروابط", "عرض ملف JSON الخام"])

    if menu == "نظرة عامة (Overview)":
        st.title(f"🚢 {data['name']}")
        st.write(data['description'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد واجهات الـ APIs", len(data['apis']))
        with col2:
            st.metric("نموذج الوصول", data['accessModel']['pricing'].capitalize())
        with col3:
            st.metric("نوع النشر", data['deliveryModel']['model'].upper())
            
        st.subheader("التصنيفات والوسوم:")
        st.write(" ".join([f"{tag}" for tag in data['tags']]))
        
        st.subheader("فريق الصيانة:")
        for m in data['maintainers']:
            st.info(f"👤 *{m['FN']}* — البريد الإلكتروني: {m['email']}")

    elif menu == "واجهات الـ APIs":
        st.title("🛠️ واجهات برمجة التطبيقات (APIs)")
        st.markdown("استعراض تفصيلي لجميع نقاط النهاية والمسارات الخاصة بنظام إدارة الموانئ:")
        
        api_selection = st.selectbox("اختر واجهة API للاستعراض:", [api['name'] for api in data['apis']])
        
        selected_api = next(api for api in data['apis'] if api['name'] == api_selection)
        
        st.subheader(selected_api['name'])
        st.write(f"*الوصف:* {selected_api['description']}")
        st.write(f"*المعرف (AID):* {selected_api['aid']}")
        st.write(f"*الرابط البشري:* [زيارة الموقع الرسمي]({selected_api['humanURL']})")
        
        st.markdown("### 📂 خصائص وملفات الـ API المرتبطة:")
        for prop in selected_api['properties']:
            st.markdown(f"- *{prop['type']}:* {prop['url']}")

    elif menu == "الموارد المشتركة والروابط":
        st.title("🔗 الموارد المشتركة وروابط النظام")
        st.markdown("قائمة بالملفات التنظيمية، سياسات الأمان، وصفحات الدعم الملحقة:")
        
        cols = st.columns(2)
        for idx, item in enumerate(data['common']):
            col = cols[idx % 2]
            with col:
                st.markdown(f"🔹 *{item['type']}*: [{item['url']}]({item['url']})")

    elif menu == "عرض ملف JSON الخام":
        st.title("📄 محتوى ملف الفهرس (JSON)")
        st.markdown("يمكنك معاينة هيكل البيانات الكامل الخاص بالمشروع هنا:")
        st.json(data),