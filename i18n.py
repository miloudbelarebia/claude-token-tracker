"""Translations for Claude Token Tracker — English, French, Arabic (MSA)."""

LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "ar": "العربية",
}

RTL_LANGS = {"ar"}

TRANSLATIONS = {
    # ─── EN ─────────────────────────────────────────────────────────────
    "en": {
        "app_title":        "Claude Token Tracker",
        "app_subtitle":     "All your Claude Code, Desktop, Cowork usage in one place",
        "live_messages":    "live · {count} messages",
        "sidebar_brand":    "Token Tracker",
        "sidebar_version":  "v1.0 · local",
        "btn_refresh":      "🔄  Refresh",
        "btn_reparse":      "⚙️  Re-parse sessions",
        "parsing":          "Parsing in progress…",

        "sec_language":     "🌐 Language",
        "sec_subscription": "💳 My Claude subscription",
        "lbl_plan":         "Plan",
        "lbl_monthly_amount":"Monthly amount",
        "lbl_currency":     "Currency",
        "per_month":        "/ month",
        "plan_help":        "Pick your plan or Custom for a free amount",

        "sec_filters":      "Filters",
        "lbl_period":       "Period",
        "range_label":      "Time range",
        "range_7d":         "Last 7 days",
        "range_30d":        "Last 30 days",
        "range_90d":        "Last 90 days",
        "range_all":        "All time",
        "range_custom":     "Custom",
        "lbl_projects":     "Projects",
        "lbl_models":       "Models",
        "lbl_entrypoints":  "Entrypoints",
        "lbl_result":       "Result",
        "messages_count":   "{count} messages",

        "kpi_you_pay":      "You pay",
        "kpi_would_cost":   "Would have cost (API)",
        "kpi_savings":      "You save",
        "kpi_roi":          "ROI",
        "kpi_plan_days":    "{plan} · {days}d",
        "kpi_sess_msgs":    "{sess} sessions · {msgs} msgs",
        "kpi_vs_api":       "vs on-demand API",

        "verdict_free":     "Free",
        "verdict_massive":  "Massively profitable",
        "verdict_very":     "Very profitable",
        "verdict_profit":   "Profitable",
        "verdict_under":    "Underused",

        "tab_roi":          "  💰 Profitability  ",
        "tab_overview":     "  📈 Overview  ",
        "tab_sessions":     "  📁 Sessions  ",
        "tab_conv":         "  💬 Conversation  ",
        "tab_search":       "  🔍 Search  ",

        "verdict_period":   "VERDICT · last {days} days",
        "verdict_body_pos": "You pay <b>{paid}</b> ({plan}, prorated) and your usage is worth <b>{api}</b> at on-demand API pricing. You save <b>{savings}</b> (×{roi} what you pay).",
        "verdict_body_neg": "You pay <b>{paid}</b> ({plan}, prorated) but your usage is only worth <b>{api}</b> at on-demand API pricing. Your subscription costs <b>{loss}</b> more than what you use.",

        "lbl_cost_per_msg":     "Cost per message",
        "lbl_real_cost_per_msg":"Your real cost / msg",
        "lbl_breakeven":        "Break-even",
        "msg_cost_avg":         "average theoretical API price",
        "msg_real_cost":        "your prorated sub / msgs",
        "msg_breakeven":        "messages to make it worth",

        "sec_cumul":        "Cumulative cost: subscription vs theoretical API",
        "trace_api_cumul":  "Theoretical API cumulative",
        "trace_sub_cumul":  "Subscription cumulative ({plan})",

        "sec_monthly":      "Monthly breakdown",
        "trace_api_month":  "Would have cost in API",
        "trace_sub_month":  "Your monthly sub",
        "col_month":        "Month",
        "col_messages":     "Messages",
        "col_api_cost":     "API cost $",
        "col_sub_cost":     "Your sub $",
        "col_savings":      "Savings",
        "col_roi":          "ROI",

        "sec_top_sessions": "Top 10 most expensive sessions (theoretical API)",
        "col_session":      "Session",
        "col_project":      "Project",
        "col_start":        "Start",
        "col_pct_sub":      "% of your sub",

        "note_title":   "ℹ️ How to read these numbers:",
        "note_paid":    "<b>You pay</b> = your monthly Claude Code subscription (fixed plan, real payment)",
        "note_api":     "<b>Would have cost (API)</b> = what your token volume would have cost at Anthropic on-demand API pricing (theoretical, public rates)",
        "note_savings": "<b>You save</b> = the difference between the two",
        "note_roi":     "<b>ROI ×N</b> = your usage is worth N times what you pay",

        "chart_daily_cost":         "Daily cost (USD)",
        "chart_tokens_breakdown":   "Token breakdown over time",
        "chart_by_model":           "Cost by model",
        "chart_by_ep":              "Cost by entrypoint",
        "chart_by_project":         "Cost by project",
        "trace_cache_read":         "Cache read",
        "trace_cache_create":       "Cache create",
        "trace_input":              "Input",
        "trace_output":             "Output",

        "sessions_list":    "Session list",
        "col_duration":     "Duration min",
        "col_begin":        "Start",
        "col_msgs":         "Msgs",

        "select_session":   "Select a session",
        "msgs_max":         "Max messages",
        "lbl_session":      "SESSION",
        "lbl_messages_cap": "MESSAGES",
        "lbl_cost_cap":     "COST",
        "lbl_input_cap":    "INPUT",
        "lbl_output_cap":   "OUTPUT",
        "lbl_cache_cap":    "CACHE",
        "truncated":        "{count} characters truncated",
        "show_first":       "Showing first {n} of {total} messages — adjust the limit above.",
        "empty_message":    "(empty)",

        "search_placeholder":   "Search in all your prompts and answers…",
        "lbl_role":             "Role",
        "role_all":             "all",
        "role_user":            "user",
        "role_assistant":       "assistant",
        "results_count":        "{count} results",

        "empty_db_warn":    "Empty database. Run first: `python3 tracker.py`",
    },

    # ─── FR ─────────────────────────────────────────────────────────────
    "fr": {
        "app_title":        "Claude Token Tracker",
        "app_subtitle":     "Tous tes usages Claude Code, Desktop, Cowork — au même endroit",
        "live_messages":    "live · {count} messages",
        "sidebar_brand":    "Token Tracker",
        "sidebar_version":  "v1.0 · local",
        "btn_refresh":      "🔄  Rafraîchir",
        "btn_reparse":      "⚙️  Re-parser les sessions",
        "parsing":          "Parsing en cours…",

        "sec_language":     "🌐 Langue",
        "sec_subscription": "💳 Mon abonnement Claude",
        "lbl_plan":         "Plan",
        "lbl_monthly_amount":"Montant mensuel",
        "lbl_currency":     "Devise",
        "per_month":        "/ mois",
        "plan_help":        "Choisis ton plan ou Custom pour un montant libre",

        "sec_filters":      "Filtres",
        "lbl_period":       "Période",
        "range_label":      "Période",
        "range_7d":         "7 derniers jours",
        "range_30d":        "30 derniers jours",
        "range_90d":        "90 derniers jours",
        "range_all":        "Tout l'historique",
        "range_custom":     "Personnalisé",
        "lbl_projects":     "Projets",
        "lbl_models":       "Modèles",
        "lbl_entrypoints":  "Entrypoints",
        "lbl_result":       "Résultat",
        "messages_count":   "{count} messages",

        "kpi_you_pay":      "Tu paies",
        "kpi_would_cost":   "Aurait coûté en API",
        "kpi_savings":      "Tu économises",
        "kpi_roi":          "ROI",
        "kpi_plan_days":    "{plan} · {days}j",
        "kpi_sess_msgs":    "{sess} sessions · {msgs} msgs",
        "kpi_vs_api":       "vs API on-demand",

        "verdict_free":     "Gratuit",
        "verdict_massive":  "Massivement rentable",
        "verdict_very":     "Très rentable",
        "verdict_profit":   "Rentable",
        "verdict_under":    "Sous-utilisé",

        "tab_roi":          "  💰 Rentabilité  ",
        "tab_overview":     "  📈 Vue d'ensemble  ",
        "tab_sessions":     "  📁 Sessions  ",
        "tab_conv":         "  💬 Conversation  ",
        "tab_search":       "  🔍 Recherche  ",

        "verdict_period":   "VERDICT · {days} derniers jours",
        "verdict_body_pos": "Tu paies <b>{paid}</b> ({plan}, prorata) et ton usage représente <b>{api}</b> en pricing API on-demand. Tu fais une économie de <b>{savings}</b> (×{roi} ce que tu paies).",
        "verdict_body_neg": "Tu paies <b>{paid}</b> ({plan}, prorata) mais ton usage ne représente que <b>{api}</b> en pricing API on-demand. Ton abo coûte <b>{loss}</b> de plus que ce que tu utilises.",

        "lbl_cost_per_msg":     "Coût par message",
        "lbl_real_cost_per_msg":"Coût réel / msg",
        "lbl_breakeven":        "Break-even",
        "msg_cost_avg":         "prix API théorique moyen",
        "msg_real_cost":        "ton abo proratisé / msgs",
        "msg_breakeven":        "messages pour rentabiliser",

        "sec_cumul":        "Coût cumulé : abo vs API théorique",
        "trace_api_cumul":  "Coût API cumulé (théorique)",
        "trace_sub_cumul":  "Abo cumulé ({plan})",

        "sec_monthly":      "Breakdown mensuel",
        "trace_api_month":  "Aurait coûté en API",
        "trace_sub_month":  "Ton abo mensuel",
        "col_month":        "Mois",
        "col_messages":     "Messages",
        "col_api_cost":     "Coût API $",
        "col_sub_cost":     "Ton abo $",
        "col_savings":      "Économies",
        "col_roi":          "ROI",

        "sec_top_sessions": "Top 10 sessions les plus chères (en API théorique)",
        "col_session":      "Session",
        "col_project":      "Projet",
        "col_start":        "Début",
        "col_pct_sub":      "% de ton abo",

        "note_title":   "ℹ️ Comment lire ces chiffres :",
        "note_paid":    "<b>Tu paies</b> = ton abo Claude Code mensuel (forfait fixe, paiement réel)",
        "note_api":     "<b>Aurait coûté en API</b> = ce que ton volume de tokens aurait coûté chez Anthropic via l'API on-demand (calcul théorique avec tarifs publics)",
        "note_savings": "<b>Tu économises</b> = différence entre les deux",
        "note_roi":     "<b>ROI ×N</b> = ton usage vaut N fois ce que tu paies",

        "chart_daily_cost":         "Coût quotidien (USD)",
        "chart_tokens_breakdown":   "Répartition des tokens dans le temps",
        "chart_by_model":           "Coût par modèle",
        "chart_by_ep":              "Coût par entrypoint",
        "chart_by_project":         "Coût par projet",
        "trace_cache_read":         "Cache read",
        "trace_cache_create":       "Cache create",
        "trace_input":              "Input",
        "trace_output":             "Output",

        "sessions_list":    "Liste des sessions",
        "col_duration":     "Durée min",
        "col_begin":        "Début",
        "col_msgs":         "Msgs",

        "select_session":   "Sélectionner une session",
        "msgs_max":         "Messages max",
        "lbl_session":      "SESSION",
        "lbl_messages_cap": "MESSAGES",
        "lbl_cost_cap":     "COÛT",
        "lbl_input_cap":    "INPUT",
        "lbl_output_cap":   "OUTPUT",
        "lbl_cache_cap":    "CACHE",
        "truncated":        "{count} caractères tronqués",
        "show_first":       "Affichage des {n} premiers messages sur {total} — ajuste la limite ci-dessus.",
        "empty_message":    "(vide)",

        "search_placeholder":   "Cherche dans tous tes prompts et réponses…",
        "lbl_role":             "Rôle",
        "role_all":             "tous",
        "role_user":            "user",
        "role_assistant":       "assistant",
        "results_count":        "{count} résultats",

        "empty_db_warn":    "Base vide. Lance d'abord : `python3 tracker.py`",
    },

    # ─── AR (Modern Standard Arabic) ────────────────────────────────────
    "ar": {
        "app_title":        "متعقّب رموز كلود",
        "app_subtitle":     "جميع استخداماتك لـ Claude Code وDesktop وCowork في مكان واحد",
        "live_messages":    "مباشر · {count} رسالة",
        "sidebar_brand":    "متعقّب الرموز",
        "sidebar_version":  "الإصدار 1.0 · محلّي",
        "btn_refresh":      "🔄  تحديث",
        "btn_reparse":      "⚙️  إعادة تحليل الجلسات",
        "parsing":          "جارٍ التحليل…",

        "sec_language":     "🌐 اللغة",
        "sec_subscription": "💳 اشتراكي في كلود",
        "lbl_plan":         "الخطة",
        "lbl_monthly_amount":"المبلغ الشهري",
        "lbl_currency":     "العملة",
        "per_month":        "/ شهريًا",
        "plan_help":        "اختر خطتك أو مخصّص لإدخال مبلغ حر",

        "sec_filters":      "التصفية",
        "lbl_period":       "الفترة",
        "range_label":      "النطاق الزمني",
        "range_7d":         "آخر 7 أيام",
        "range_30d":        "آخر 30 يومًا",
        "range_90d":        "آخر 90 يومًا",
        "range_all":        "كل الفترة",
        "range_custom":     "مخصّص",
        "lbl_projects":     "المشاريع",
        "lbl_models":       "النماذج",
        "lbl_entrypoints":  "نقاط الدخول",
        "lbl_result":       "النتيجة",
        "messages_count":   "{count} رسالة",

        "kpi_you_pay":      "ما تدفعه",
        "kpi_would_cost":   "كان سيكلّفك (API)",
        "kpi_savings":      "ما توفّره",
        "kpi_roi":          "العائد",
        "kpi_plan_days":    "{plan} · {days} يوم",
        "kpi_sess_msgs":    "{sess} جلسة · {msgs} رسالة",
        "kpi_vs_api":       "مقابل API عند الطلب",

        "verdict_free":     "مجّاني",
        "verdict_massive":  "مربح بشكل كبير جدًا",
        "verdict_very":     "مربح جدًا",
        "verdict_profit":   "مربح",
        "verdict_under":    "غير مستغَل",

        "tab_roi":          "  💰 الربحية  ",
        "tab_overview":     "  📈 نظرة عامة  ",
        "tab_sessions":     "  📁 الجلسات  ",
        "tab_conv":         "  💬 المحادثة  ",
        "tab_search":       "  🔍 البحث  ",

        "verdict_period":   "الحكم · آخر {days} يوم",
        "verdict_body_pos": "أنت تدفع <b>{paid}</b> ({plan}، تناسبيًا) واستخدامك يساوي <b>{api}</b> بأسعار API عند الطلب. توفّر <b>{savings}</b> (×{roi} ما تدفعه).",
        "verdict_body_neg": "أنت تدفع <b>{paid}</b> ({plan}، تناسبيًا) لكن استخدامك لا يساوي سوى <b>{api}</b> بأسعار API عند الطلب. اشتراكك يكلّفك <b>{loss}</b> أكثر مما تستخدمه.",

        "lbl_cost_per_msg":     "تكلفة الرسالة",
        "lbl_real_cost_per_msg":"تكلفتك الحقيقية / رسالة",
        "lbl_breakeven":        "نقطة التعادل",
        "msg_cost_avg":         "متوسط سعر API النظري",
        "msg_real_cost":        "اشتراكك التناسبي / الرسائل",
        "msg_breakeven":        "رسالة لتغطية الاشتراك",

        "sec_cumul":        "التكلفة التراكمية: الاشتراك مقابل API النظري",
        "trace_api_cumul":  "تكلفة API التراكمية (نظري)",
        "trace_sub_cumul":  "الاشتراك التراكمي ({plan})",

        "sec_monthly":      "التفصيل الشهري",
        "trace_api_month":  "كان سيكلّفك في API",
        "trace_sub_month":  "اشتراكك الشهري",
        "col_month":        "الشهر",
        "col_messages":     "الرسائل",
        "col_api_cost":     "تكلفة API $",
        "col_sub_cost":     "اشتراكك $",
        "col_savings":      "التوفير",
        "col_roi":          "العائد",

        "sec_top_sessions": "أكثر 10 جلسات تكلفةً (API نظري)",
        "col_session":      "الجلسة",
        "col_project":      "المشروع",
        "col_start":        "البداية",
        "col_pct_sub":      "٪ من اشتراكك",

        "note_title":   "ℹ️ كيف تقرأ هذه الأرقام:",
        "note_paid":    "<b>ما تدفعه</b> = اشتراكك الشهري في Claude Code (خطة ثابتة، دفع حقيقي)",
        "note_api":     "<b>كان سيكلّفك (API)</b> = ما كان حجم رموزك سيكلّفه عبر API عند الطلب من Anthropic (نظري، أسعار عامة)",
        "note_savings": "<b>ما توفّره</b> = الفرق بين الاثنين",
        "note_roi":     "<b>العائد ×N</b> = استخدامك يساوي N ضعف ما تدفعه",

        "chart_daily_cost":         "التكلفة اليومية (USD)",
        "chart_tokens_breakdown":   "توزيع الرموز عبر الزمن",
        "chart_by_model":           "التكلفة حسب النموذج",
        "chart_by_ep":              "التكلفة حسب نقطة الدخول",
        "chart_by_project":         "التكلفة حسب المشروع",
        "trace_cache_read":         "قراءة الذاكرة المؤقتة",
        "trace_cache_create":       "إنشاء الذاكرة المؤقتة",
        "trace_input":              "المدخل",
        "trace_output":             "المخرج",

        "sessions_list":    "قائمة الجلسات",
        "col_duration":     "المدة بالدقائق",
        "col_begin":        "البداية",
        "col_msgs":         "الرسائل",

        "select_session":   "اختر جلسة",
        "msgs_max":         "الحد الأقصى للرسائل",
        "lbl_session":      "الجلسة",
        "lbl_messages_cap": "الرسائل",
        "lbl_cost_cap":     "التكلفة",
        "lbl_input_cap":    "المدخل",
        "lbl_output_cap":   "المخرج",
        "lbl_cache_cap":    "الذاكرة المؤقتة",
        "truncated":        "تم اقتطاع {count} حرفًا",
        "show_first":       "عرض أول {n} من أصل {total} رسالة — اضبط الحد أعلاه.",
        "empty_message":    "(فارغ)",

        "search_placeholder":   "ابحث في جميع طلباتك وردودك…",
        "lbl_role":             "الدور",
        "role_all":             "الكل",
        "role_user":            "المستخدم",
        "role_assistant":       "المساعد",
        "results_count":        "{count} نتيجة",

        "empty_db_warn":    "قاعدة البيانات فارغة. شغّل أوّلًا: `python3 tracker.py`",
    },
}


def make_translator(lang: str):
    """Return a t(key, **kwargs) function for the given language."""
    table = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    fallback = TRANSLATIONS["en"]
    def t(key: str, **kwargs) -> str:
        val = table.get(key) or fallback.get(key) or key
        if kwargs:
            try:
                return val.format(**kwargs)
            except (KeyError, IndexError):
                return val
        return val
    return t


def is_rtl(lang: str) -> bool:
    return lang in RTL_LANGS
