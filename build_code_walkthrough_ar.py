"""Arabic code-walkthrough deck: every code cell of the notebook, with what it does and why (for the project video).

The code shown on each slide is read directly from Mid-Project-Script.ipynb, so the deck always matches the notebook.
"""
import re
from pathlib import Path

import nbformat
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

from pptx_ar_utils import ArabicDeck, NAVY, NAVY_2, SKY, ORANGE, ICE, WHITE, INK, MUTED, LIGHT_MUTED

PROJECT = Path(__file__).parent
NOTEBOOK = PROJECT / "Mid-Project-Script.ipynb"
OUT = PROJECT / "Airline_Satisfaction_Code_Walkthrough_AR.pptx"

code_cells = [c.source for c in nbformat.read(NOTEBOOK, as_version=4).cells if c.cell_type == "code"]
TOTAL_CELLS = len(code_cells)
FUNCTION_COUNT = sum(len(re.findall(r"^def ", source, flags=re.M)) for source in code_cells)

# Sections of the notebook: the first code cell of each section -> (section name, what happens in it)
SECTIONS = {
    1: ("الإعداد", "استيراد المكتبات، ضبط شكل الرسوم، وتثبيت الألوان والمسارات"),
    2: ("جمع البيانات وتقييمها", "تحميل الملف، ثم البحث عن كل مشاكل الجودة قبل لمس البيانات"),
    12: ("تنظيف البيانات", "إصلاح كل مشكلة بطريقة Define → Code → Test وحفظ البيانات النظيفة"),
    23: ("التحليل أحادي المتغير", "دراسة كل متغير وحده: الرضا، الشرائح، العمر، المسافة، التأخير، الخدمات"),
    30: ("التحليل ثنائي ومتعدد المتغيرات", "ربط المتغيرات بالرضا والإجابة على الأسئلة مع اختبارات إحصائية"),
    42: ("الخلاصة", "تلخيص قوة كل عامل في جدول ورسم ختامي"),
}

# (cell number, (first line, last line) or None for the whole cell, title, what it does, why)
WALKTHROUGH = [
    (1, (1, 13), "استيراد المكتبات",
     ["numpy و pandas للتعامل مع البيانات", "matplotlib و seaborn للرسوم، و scipy.stats للاختبارات الإحصائية",
      "إخفاء رسائل التحذير"],
     ["كل مكتبة لها دور محدد في المشروع", "إخفاء التحذيرات يجعل النوتبوك نظيفًا ومقروءًا"]),
    (1, (15, 29), "ضبط الشكل والثوابت",
     ["ثيم whitegrid وحجم افتراضي للرسوم وعناوين عريضة، وإظهار كل الأعمدة",
      "ألوان ثابتة: أزرق = راضٍ، برتقالي = غير راضٍ", "مسارات الملفات في ثوابت DATA_PATH و CLEAN_DATA_PATH"],
     ["نفس اللون لنفس الفئة في كل الرسوم فلا يتلخبط القارئ", "الثوابت تمنع تكرار القيم وتسهّل التعديل من مكان واحد"]),
    (2, None, "تحميل البيانات",
     ["قراءة ملف Data.csv في DataFrame اسمه raw_df", "طباعة عدد الصفوف والأعمدة وعرض أول 5 صفوف"],
     ["أول نظرة على البيانات والتأكد أن التحميل صحيح: 25,976 صفًا و 25 عمودًا"]),
    (3, None, "معلومات الأعمدة",
     ["info() تعرض نوع كل عمود وعدد القيم غير الفارغة"],
     ["كشفت أن Arrival Delay فيه 83 قيمة ناقصة ومخزّن كرقم عشري float"]),
    (4, None, "دالة تقرير الجودة",
     ["دالة quality_report ترجع جدولًا لكل عمود: النوع، عدد ونسبة القيم الناقصة، عدد القيم المختلفة، ومثال"],
     ["دالة نعيد استخدامها قبل التنظيف وبعده للمقارنة", "استخدام الدوال لتجنب التكرار من معايير التقييم"]),
    (5, None, "فحص التكرار",
     ["عدد الصفوف المكررة، وعدد أرقام id المكررة",
      "التحقق هل عمود Unnamed: 0 مجرد ترقيم من 0 إلى n-1"],
     ["النتيجة: لا يوجد أي تكرار", "Unnamed: 0 ليس له معنى، لذلك سيُحذف في التنظيف"]),
    (6, None, "فحص القيم النصية",
     ["value_counts لكل عمود نصي لعرض القيم الموجودة وعددها"],
     ["كشف التسميات غير المتسقة: disloyal Customer بحرف صغير، Business travel، والاختصار Eco"]),
    (7, None, "الملخص الإحصائي",
     ["describe() تعطي المتوسط والانحراف وأقل وأكبر قيمة والربيعيات لكل عمود رقمي، و .T تقلب الجدول"],
     ["لاحظنا أن أقل تقييم = 0 رغم أن المقياس من 1 إلى 5", "وأن أكبر تأخير 1,128 دقيقة"]),
    (8, None, "التقييمات بصفر",
     ["تحديد أعمدة الخدمات الـ 14 بالـ slicing بين أول وآخر اسم", "عدّ الأصفار في كل خدمة وترتيبها"],
     ["الصفر يعني «لا ينطبق»؛ لو تُرك سيخفض المتوسط بشكل خاطئ",
      "أكثرها: ملاءمة المواعيد (1,381) والحجز أونلاين (1,195)"]),
    (9, None, "رسم القيم المتطرفة",
     ["حلقة for ترسم box plot لكل عمود من الأعمدة الرقمية الأربعة في شكل واحد"],
     ["الـ box plot أسرع طريقة لرؤية القيم المتطرفة بالعين", "حلقة واحدة بدل كتابة نفس الكود أربع مرات"]),
    (10, None, "عدّ القيم المتطرفة",
     ["دالة تحسب حدود IQR: من Q1 − 1.5×IQR إلى Q3 + 1.5×IQR، وتعد القيم خارجها",
      "تطبيقها على الأعمدة الأربعة في Series واحدة"],
     ["نحوّل ما رأيناه في الرسم إلى أرقام: حوالي 3,500 قيمة متطرفة في التأخير و 584 في المسافة"]),
    (11, None, "هل التأخيرات الكبيرة حقيقية؟",
     ["حساب معامل الارتباط بين تأخير الإقلاع وتأخير الوصول"],
     ["الارتباط 0.965: الاثنان يتحركان معًا، إذن القيم الكبيرة حقيقية وليست أخطاء إدخال",
      "وهذا سيبرر لاحقًا طريقة ملء القيم الناقصة"]),
    (12, None, "نسخة للعمل عليها",
     ["إنشاء clean_df كنسخة من raw_df"],
     ["نحافظ على البيانات الأصلية كما هي للمقارنة والرجوع إليها"]),
    (13, None, "حذف العمود بلا فائدة",
     ["حذف Unnamed: 0 ثم اختبار ذلك بـ assert وطباعة عدد الأعمدة"],
     ["Define → Code → Test: كل إصلاح يتبعه اختبار يضمن أنه نجح"]),
    (14, None, "توحيد أسماء الأعمدة",
     ["دالة to_snake_case: حروف صغيرة، استبدال / و - بمسافة، حذف in minutes، ثم المسافات إلى _",
      "تطبيقها على كل الأعمدة بـ list comprehension"],
     ["أسماء بدون مسافات أسهل في الكتابة وأقل أخطاء", "دالة واحدة بدل تعديل 24 اسمًا يدويًا"]),
    (15, None, "قائمة الخدمات وأسماء الرسوم",
     ["حفظ أسماء أعمدة الخدمات الجديدة في service_columns",
      "دالة pretty_name تعيد الاسم إلى شكل مقروء مثل Seat Comfort"],
     ["القائمة تُستخدم في كل التحليل", "الرسوم تحتاج عناوين مفهومة وليس snake_case"]),
    (16, (1, 6), "قاموس التسميات الموحدة",
     ["قاموس لكل عمود: القيمة القديمة ← القيمة الجديدة", "مثال: disloyal Customer ← Disloyal Customer و Eco ← Economy"],
     ["كل التعديلات في مكان واحد واضح وسهل المراجعة"]),
    (16, (8, 22), "دالة توحيد التسميات",
     ["standardise_labels: لكل عمود تبحث عن قيم غير موجودة في القاموس، ولو وجدت ترفع خطأ، ثم تطبق map",
      "الاختبار يطبع القيم الفريدة بعد التعديل"],
     ["map تحوّل أي قيمة غير معرّفة إلى NaN بصمت؛ هذا الفحص يمنع فقدان بيانات دون أن ننتبه"]),
    (17, None, "ملء التأخير الناقص",
     ["ملء القيم الناقصة في arrival_delay بقيمة departure_delay لنفس الراكب، ثم التحويل إلى int",
      "اختبار: عدد الناقص قبل وبعد، ونوع العمود"],
     ["الارتباط 0.96، فتأخير الإقلاع أدق تقدير من المتوسط أو الوسيط", "التأخير بالدقائق عدد صحيح"]),
    (18, None, "الصفر = لا ينطبق",
     ["عمود جديد not_applicable_count يعد إجابات «لا ينطبق» لكل راكب",
      "replace(0, np.nan) في أعمدة الخدمات، ثم التأكد أن المدى أصبح من 1 إلى 5"],
     ["قيم NaN تُتجاهل تلقائيًا في حساب المتوسط", "ولم نفقد المعلومة لأننا عددناها أولًا"]),
    (19, None, "إضافة أعمدة جديدة",
     ["pd.cut لتقسيم العمر إلى 5 فئات، والمسافة إلى 3، والتأخير إلى 4",
      "متوسط تقييم الخدمات لكل راكب، و is_satisfied = 1 أو 0"],
     ["الفئات تسهّل مقارنة الشرائح", "مع is_satisfied تصبح نسبة الرضا = المتوسط mean مباشرة"]),
    (20, None, "تحويل النصوص إلى Category",
     ["تحويل الأعمدة النصية إلى Categorical بترتيب محدد، والدرجة مرتبة: Economy ثم Economy Plus ثم Business",
      "قياس الذاكرة قبل وبعد"],
     ["الترتيب يظهر صحيحًا في الجداول والرسوم", "الذاكرة انخفضت من 6.9 إلى 4.6 ميجابايت"]),
    (21, None, "الفحص النهائي",
     ["طباعة الأبعاد وتشغيل quality_report مرة أخرى على البيانات النظيفة"],
     ["التأكد أن الناقص الوحيد هو NaN المقصودة (لا ينطبق)", "النتيجة 25,976 صفًا و 30 عمودًا"]),
    (22, None, "حفظ البيانات النظيفة",
     ["حفظ clean_df في Data_Cleaned.csv بدون عمود index"],
     ["لوحة Streamlit تقرأ هذا الملف، فيبقى التنظيف منفصلًا عن العرض"]),
    (23, None, "الرضا العام برسم Pie",
     ["جدول بعدد ونسبة كل فئة رضا", "رسم pie بالألوان الثابتة من القاموس"],
     ["يجيب السؤال الأول: 43.9% فقط راضون", "الـ pie مناسب لأن عندنا فئتين فقط"]),
    (24, None, "شرائح الركاب برسم Bar",
     ["دالة plot_category_counts ترسم أعمدة لعمود فئوي ومكتوب على كل عمود العدد والنسبة",
      "حلقة ترسمها لأربعة أعمدة في شبكة 2×2"],
     ["دالة واحدة بدل تكرار نفس الكود أربع مرات", "الأرقام على الأعمدة تغني عن تخمين القيم"]),
    (25, None, "العمر والمسافة برسم Histogram",
     ["دالة plot_numeric_distribution: histogram مع منحنى KDE وخطين للمتوسط والوسيط",
      "تطبيقها على العمر والمسافة، ثم جدول mean و median و std و skew"],
     ["الفرق بين المتوسط والوسيط يكشف الالتواء", "المسافة ملتوية لليمين: الوسيط 849 والمتوسط 1,194"]),
    (26, None, "التأخير بمقياس لوغاريتمي",
     ["histogram لكل عمود تأخير مع محور y لوغاريتمي set_yscale(\"log\")"],
     ["أغلب القيم صفر وقليل منها كبير جدًا؛ بدون log لن يظهر إلا عمود واحد"]),
    (27, None, "نسبة الالتزام بالمواعيد",
     ["نسبة الرحلات بدون تأخير، وتوزيع فئات التأخير كنسب مئوية"],
     ["56.3% من الرحلات تصل في موعدها، و 6.8% تتأخر أكثر من ساعة"]),
    (28, None, "متوسط تقييم الخدمات",
     ["متوسط كل خدمة مرتب في أعمدة أفقية، البرتقالي للخدمات تحت المتوسط العام",
      "خط متقطع للمتوسط العام والقيمة مكتوبة على كل عمود"],
     ["يوضح أضعف الخدمات: الواي فاي 2.81 والحجز أونلاين 2.89"]),
    (29, None, "توزيع التقييمات برسم Heatmap",
     ["لكل خدمة نسبة كل تقييم من 1 إلى 5 بـ apply و value_counts(normalize=True)", "عرضها كخريطة حرارية"],
     ["المتوسط وحده يخفي التوزيع؛ الخريطة توضح كم شخصًا أعطى 1 أو 5"]),
    (30, (1, 14), "دوال الاختبارات الإحصائية",
     ["chi_square_test: جدول تقاطعي ثم chi2_contingency، وحساب Cramér's V لقوة العلاقة",
      "mann_whitney_test: يقارن عمودًا رقميًا بين الراضين وغير الراضين ويرجع الوسيطين و p-value"],
     ["كل استنتاج يحتاج دليلًا إحصائيًا", "Mann-Whitney لأن البيانات ملتوية وليست طبيعية، و V لأن p وحدها لا تقيس قوة العلاقة"]),
    (30, (16, 33), "دوال نسبة الرضا والرسم المكدس",
     ["satisfaction_rate: groupby ثم متوسط is_satisfied × 100 مع عدد الركاب",
      "plot_satisfaction_split: أعمدة مكدسة 100% والنسب مكتوبة داخلها"],
     ["دوال تُستخدم في كل الأسئلة من الثاني إلى السادس بدل تكرار الكود"]),
    (31, None, "الرضا حسب الشرائح",
     ["حلقة ترسم plot_satisfaction_split للنوع والولاء ونوع السفر والدرجة، مع مفتاح ألوان مشترك"],
     ["مقارنة مباشرة: البيزنس 70% مقابل الإيكونومي 19%، والنوع بلا فرق"]),
    (32, None, "جدول الاختبارات",
     ["تطبيق chi_square_test على 7 أعمدة في DataFrame واحد",
      "عمود significant عندما p < 0.05، ثم الترتيب حسب Cramér's V"],
     ["يرتب العوامل حسب قوتها: الدرجة 0.50، نوع السفر 0.45", "النوع غير معنوي (p = 0.24)"]),
    (33, (1, 6), "العمر والرضا برسم Violin",
     ["violin plot لتوزيع العمر لكل مجموعة رضا مع خطوط الربيعيات"],
     ["يوضح شكل التوزيع كاملًا وليس المتوسط فقط: الراضون أكبر سنًا"]),
    (33, (8, 22), "نسبة الرضا عبر الأعمار",
     ["نسبة الرضا لكل سنة عمر مع متوسط متحرك 5 سنوات وخط للمتوسط العام",
      "جدول الفئات العمرية واختبار Mann-Whitney للعمر"],
     ["المتوسط المتحرك يزيل التذبذب", "الاختبار يؤكد الفرق: وسيط 43 مقابل 37 و p < 0.001"]),
    (34, None, "مقارنة الخدمات",
     ["متوسط كل خدمة لكل مجموعة رضا، وعمود gap للفرق",
      "ارتباط Spearman بين كل خدمة و is_satisfied"],
     ["Spearman مناسب للتقييمات الترتيبية", "أكبر فجوة: الصعود أونلاين +1.44"]),
    (35, None, "رسم الفجوة Dumbbell",
     ["لكل خدمة نقطتان (برتقالي وأزرق) يربطهما خط، وقيمة الفجوة مكتوبة بجانبها"],
     ["رسم الـ dumbbell يوضح حجم الفجوة أفضل من أعمدة متجاورة"]),
    (36, None, "أثر كل درجة تقييم",
     ["لأهم 4 خدمات: نسبة الرضا عند كل تقييم من 1 إلى 5 كخطوط"],
     ["يظهر القفزة عند تقييم 4 و 5", "من قيّم الواي فاي بـ 5 راضٍ بنسبة 98.8%"]),
    (37, None, "مصفوفة الارتباط",
     ["ارتباط Spearman بين كل الخدمات و is_satisfied",
      "قناع np.triu لإخفاء النصف المكرر، وألوان RdBu متباعدة حول الصفر"],
     ["يكشف الخدمات المرتبطة ببعضها، والخدمات الأقوى ارتباطًا بالرضا"]),
    (38, (1, 12), "الرضا حسب التأخير",
     ["نسبة الرضا لكل فئة تأخير وعرضها كأعمدة والقيم مكتوبة عليها"],
     ["يجيب السؤال الرابع: من 47.9% في الموعد إلى 35.2% بعد أكثر من ساعة"]),
    (38, (14, 27), "الإقلاع مقابل الوصول برسم Scatter",
     ["scatter لعينة 4,000 رحلة متأخرة بمقياس لوغاريتمي ملونة بالرضا",
      "اختبار Mann-Whitney لعمودي التأخير"],
     ["العينة تمنع تكدّس النقاط", "الفرق معنوي لكن ضعيف (V ≈ 0.10)"]),
    (39, (1, 7), "المسافة حسب الدرجة برسم Box",
     ["box plot لمسافة الرحلة لكل درجة، مقسمة حسب الرضا"],
     ["يظهر أن رحلات البيزنس أطول بكثير من الإيكونومي"]),
    (39, (9, 21), "المسافة × الدرجة برسم Heatmap",
     ["pivot_table لنسبة الرضا لكل مزيج مسافة × درجة، معروضة كخريطة حرارية",
      "جدول الوسيط لكل درجة واختبار المسافة"],
     ["يكشف العامل الخفي: داخل الإيكونومي المسافة لا تؤثر تقريبًا (17–21%)"]),
    (40, (1, 12), "نوع السفر × الدرجة",
     ["جدولا pivot: واحد للنسبة وآخر لعدد الركاب، ودمجهما كنص على كل خلية في الخريطة"],
     ["كتابة n على كل خلية تمنع الاستنتاج من مجموعات صغيرة"]),
    (40, (14, 26), "الولاء × نوع السفر",
     ["groupby على عمودين ثم unstack لرسم أعمدة مجمعة والقيم مكتوبة عليها"],
     ["يوضح أن الولاء لا يساعد المسافرين لأسباب شخصية: 10% فقط راضون"]),
    (41, None, "نظرة متعددة المتغيرات",
     ["عينة 6,000 راكب وثلاثة رسوم scatter (رسم لكل درجة): العمر مقابل متوسط التقييم، ملونة بالرضا"],
     ["أربعة متغيرات في رسم واحد", "في كل درجة، الراضون أعلى في متوسط التقييم"]),
    (42, None, "جدول العوامل",
     ["DataFrame بالعوامل وقيمة Cramér's V لكل منها بإعادة استخدام chi_square_test",
      "تصنيف القوة بـ pd.cut: ضئيل، ضعيف، متوسط، قوي"],
     ["ملخص رقمي واحد لكل النتائج"]),
    (43, None, "ما الذي يؤثر أكثر؟",
     ["أعمدة أفقية مرتبة لقوة كل عامل مع القيمة مكتوبة"],
     ["رسم ختامي يجيب على السؤال الأهم في نظرة واحدة"]),
]


def code_lines(cell_number, line_range):
    """Return the code of a notebook cell, or only the given (first, last) 1-based line range."""
    lines = code_cells[cell_number - 1].split("\n")
    if line_range:
        first, last = line_range
        lines = lines[first - 1:last]
    return "\n".join(lines)


def section_slide(deck, number, name, description):
    s = deck.dark_slide()
    deck.shape(s, MSO_SHAPE.OVAL, 9.6, 1.5, 4.4, 4.4, NAVY_2)
    deck.text(s, 9.6, 2.85, 4.4, 1.4, str(number), size=96, color=SKY, bold=True, rtl=False,
              align=PP_ALIGN.CENTER)
    deck.text(s, 0.8, 2.6, 8.4, 0.5, "قسم من النوتبوك", size=17, color=LIGHT_MUTED, bold=True)
    deck.text(s, 0.8, 3.1, 8.4, 1.1, name, size=44, color=WHITE, bold=True)
    deck.text(s, 0.8, 4.3, 8.4, 1.0, description, size=19, color=LIGHT_MUTED)
    deck.notes(s, f"ننتقل الآن إلى قسم {name}: {description}.")


def cell_slide(deck, cell_number, line_range, title, what, why, section_name):
    code = code_lines(cell_number, line_range)
    part = ""
    if line_range:
        parts = [r for (c, r, *_rest) in WALKTHROUGH if c == cell_number]
        part = f" · الجزء {parts.index(line_range) + 1} من {len(parts)}"
    s = deck.content_slide(title, f"{section_name} · الخلية {cell_number} من {TOTAL_CELLS}{part}")
    n_lines = len(code.split("\n"))
    code_height = min(3.75, max(1.0, n_lines * 0.21 + 0.45))
    deck.code_block(s, 0.6, 1.5, 12.13, code_height, code)
    cards_y = 1.5 + code_height + 0.25
    cards_h = min(6.85 - cards_y, 2.3)
    for x, w, heading, items, color in [(0.6, 6.0, "ماذا يفعل الكود؟", what, SKY),
                                        (6.75, 5.98, "لماذا؟", why, ORANGE)]:
        deck.card(s, x, cards_y, w, cards_h)
        deck.text(s, x + 0.25, cards_y + 0.15, w - 0.5, cards_h - 0.25,
                  [(heading, {"bold": True, "color": color, "size": 16, "space_after": 6})]
                  + [(f"•  {item}", {"space_after": 4}) for item in items], size=14, color=INK)
    deck.notes(s, f"{title}. " + " ".join(what) + ". والسبب: " + " ".join(why) + ".")


def build():
    covered = {cell for cell, *_rest in WALKTHROUGH}
    assert covered == set(range(1, TOTAL_CELLS + 1)), f"cells not explained: {set(range(1, TOTAL_CELLS + 1)) - covered}"
    deck = ArabicDeck("شرح كود مشروع رضا ركاب الطيران — خلية بخلية")

    # Title
    s = deck.dark_slide()
    deck.mirror = False   # title layout is already designed right-to-left
    deck.shape(s, MSO_SHAPE.OVAL, -1.6, -1.2, 6.4, 6.4, NAVY_2)
    deck.shape(s, MSO_SHAPE.OVAL, 0.6, 3.9, 3.4, 3.4, SKY)
    deck.text(s, 0.6, 4.95, 3.4, 0.8, str(TOTAL_CELLS), size=48, color=WHITE, bold=True, rtl=False,
              align=PP_ALIGN.CENTER)
    deck.text(s, 0.6, 5.8, 3.4, 0.4, "خلية كود", size=16, color=WHITE, align=PP_ALIGN.CENTER)
    deck.text(s, 4.5, 1.3, 8.2, 0.4, "المشروع المرحلي  ·  شرح الكود", size=16, color=LIGHT_MUTED, bold=True)
    deck.text(s, 4.5, 1.9, 8.2, 2.0, "شرح الكود بالكامل\nخلية بخلية", size=50, color=WHITE, bold=True)
    deck.text(s, 4.5, 4.1, 8.2, 0.8, "ماذا يفعل كل جزء من الكود؟ ولماذا كُتب بهذه الطريقة؟", size=20,
              color=LIGHT_MUTED)
    deck.text(s, 4.5, 5.6, 8.2, 0.4, "هشام محمد", size=20, color=WHITE, bold=True)
    deck.text(s, 4.5, 6.1, 8.2, 0.4, "Epsilon AI  ·  برنامج علوم البيانات", size=14, color=LIGHT_MUTED)
    deck.mirror = True
    deck.notes(s, "في هذا الفيديو سأشرح كود المشروع بالكامل، خلية بخلية، بنفس ترتيب النوتبوك: ماذا تفعل كل خلية، "
                  "ولماذا كتبتها بهذه الطريقة.")

    # Map of the notebook
    s = deck.content_slide("خريطة النوتبوك", "المحتوى")
    starts = sorted(SECTIONS)
    for i, start in enumerate(starts):
        end = (starts[i + 1] - 1) if i + 1 < len(starts) else TOTAL_CELLS
        name, description = SECTIONS[start]
        y = 1.65 + i * 0.86
        deck.badge(s, 0.6, y, str(i + 1), fill=SKY if i % 2 == 0 else NAVY)
        deck.text(s, 1.4, y - 0.03, 7.0, 0.4, name, size=20, color=NAVY, bold=True)
        deck.text(s, 1.4, y + 0.36, 7.0, 0.4, description, size=13, color=MUTED)
        deck.card(s, 8.6, y + 0.02, 4.13, 0.62)
        deck.text(s, 8.8, y + 0.13, 3.73, 0.4, f"الخلايا من {start} إلى {end}", size=14, color=NAVY)
    deck.notes(s, "النوتبوك مقسّم إلى ستة أقسام، وسأمر عليها بالترتيب.")

    section_counter = 0
    current_section = None
    for cell_number, line_range, title, what, why in WALKTHROUGH:
        if cell_number in SECTIONS and (line_range is None or line_range[0] == 1):
            section_counter += 1
            current_section = SECTIONS[cell_number][0]
            section_slide(deck, section_counter, *SECTIONS[cell_number])
        cell_slide(deck, cell_number, line_range, title, what, why, current_section)

    # Closing
    s = deck.dark_slide()
    deck.text(s, 0.8, 1.0, 11.8, 0.5, "الملخص", size=17, color=LIGHT_MUTED, bold=True)
    deck.text(s, 0.8, 1.5, 11.8, 1.0, "كود منظم، موثق، وقابل لإعادة التشغيل", size=36, color=WHITE, bold=True)
    for i, (num, lab) in enumerate([(str(TOTAL_CELLS), "خلية كود تعمل بدون أخطاء"),
                                    (str(FUNCTION_COUNT), "دالة لتجنب تكرار الكود"),
                                    ("10", "أنواع رسوم مختلفة")]):
        x = 0.8 + i * 4.0
        deck.shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 3.0, 3.7, 2.2, NAVY_2)
        deck.text(s, x + 0.3, 3.3, 3.1, 0.9, num, size=40, color=WHITE, bold=True, rtl=False, align=PP_ALIGN.RIGHT)
        deck.text(s, x + 0.3, 4.3, 3.1, 0.7, lab, size=16, color=LIGHT_MUTED)
    deck.text(s, 0.8, 5.8, 11.8, 0.8, "شكرًا لحسن الاستماع — الكود والبيانات على GitHub", size=20, color=WHITE)
    deck.notes(s, "هذا كل الكود. النوتبوك يعمل من البداية للنهاية بدون أخطاء، ويستخدم الدوال لتجنب التكرار، "
                  "وكل خطوة موثقة. شكرًا لحسن الاستماع.")

    return deck.save(OUT)


if __name__ == "__main__":
    print("saved", OUT, build(), "slides")
