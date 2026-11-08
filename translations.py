"""All product copy lives here. Add matching keys to both languages."""

from vehicle import MAX_YEAR, MIN_YEAR
from report_translations import REPORT_TEXT
from home_translations import HOME_TEXT
from symptom_translations import SYMPTOM_TEXT

LANGUAGES = {"az": "Azərbaycan dili", "en": "English"}

TEXT = {
    "az": {
        "select_manufacturer": "İstehsalçını seçin və ya axtarın",
        "select_model": "Modeli seçin və ya axtarın",
        "select_manufacturer_first": "Əvvəlcə istehsalçını seçin",
        "select_year": "Buraxılış ilini seçin",
        "not_listed": "Digər / Siyahıda yoxdur",
        "manual_manufacturer": "İstehsalçının adını daxil edin",
        "manual_model_label": "Modelin adını daxil edin",
        "catalog_limit": "Kataloq tam deyil; siyahıda olmayan adları əl ilə daxil edə bilərsiniz. İl seçimi modelin həmin ildə istehsalını, mühərrikini və ya kod uyğunluğunu təsdiqləmir.",
        "language": "İnterfeys dili",
        "eyebrow": "İNTERNETSİZ OBD-II KÖMƏKÇİSİ · V0.3",
        "hero_title": "Hər detal önəmlidir.",
        "hero_description": "Avtomobil məlumatlarınızı daxil edin. OBD-II kodlarının mənasını, mümkün səbəbləri və təhlükəsiz növbəti addımları nəzərdən keçirin.",
        "status": "10 yerli kod · İnternetsiz",
        "vehicle_title": "Avtomobil haqqında",
        "vehicle_subtitle": "Dəqiq məlumat daha aydın başlanğıc deməkdir.",
        "required_note": "Ulduz (*) işarəli sahələr mütləq doldurulmalıdır.",
        "manufacturer": "İstehsalçı",
        "manufacturer_placeholder": "Məsələn, Toyota",
        "model": "Model",
        "model_placeholder": "Məsələn, Corolla",
        "year": "Buraxılış ili",
        "year_placeholder": "Məsələn, 2020",
        "engine_type": "Mühərrik növü",
        "engine_placeholder": "Mühərrik növünü seçin",
        "gasoline": "Benzin", "diesel": "Dizel", "hybrid": "Hibrid", "electric": "Elektrik",
        "displacement": "Mühərrik həcmi",
        "displacement_label": "Mühərrik həcmi (L, istəyə bağlı)",
        "displacement_placeholder": "Məsələn, 1,6",
        "mileage": "Yürüş",
        "mileage_label": "Yürüş (km, istəyə bağlı)",
        "mileage_placeholder": "Məsələn, 85000",
        "symptoms_title": "Nə müşahidə edirsiniz?",
        "symptoms_subtitle": "Səs, titrəmə, xəbərdarlıq işıqları və ya davranış dəyişikliyi.",
        "symptoms": "Əlamətlərin təsviri",
        "symptoms_placeholder": "Nə baş verir? Nə vaxt başlayıb? Hansı şəraitdə təkrarlanır?",
        "symptoms_hint": "Əlamətlərin nə vaxt və hansı şəraitdə yarandığını qeyd edin.",
        "obd_code": "OBD-II kodu",
        "obd_label": "OBD-II nasazlıq kodları (istəyə bağlı)",
        "obd_placeholder": "Məsələn, P0301, P0171",
        "obd_hint": "Kodları vergüllə ayırın. Yalnız yerli bazadakı 10 kod izah olunur; təkcə əlamətlərə əsaslanan təhlil hələ yoxdur.",
        "analyze": "Avtomobili təhlil et",
        "submit_hint": "İlkin hesabat yerli kod məlumatlarından və sabit qaydalardan hazırlanır.",
        "guide_title": "Aydın başlanğıc, üç addım",
        "step1_title": "Avtomobili tanıdaq", "step1_body": "Əsas texniki məlumatları əlavə edin.",
        "step2_title": "Əlamətləri təsvir edək", "step2_body": "Müşahidələrinizi öz sözlərinizlə yazın.",
        "step3_title": "Hesabatı nəzərdən keçirək", "step3_body": "Kod izahlarını, təhlükəsizlik qeydlərini və məhdudiyyətləri oxuyun.",
        "scope_title": "Bu versiya haqqında",
        "scope_body": "V0.3 yerli kod bazasından istifadə edir. Generativ AI yoxdur. Mümkün səbəblər təsdiqlənmiş diaqnoz deyil.",
        "privacy_title": "Bu brauzer sessiyasında",
        "privacy_body": "Məlumatlar bu sessiyada saxlanır, məlumat bazasına yazılmır və AI xidmətinə göndərilmir.",
        "summary_title": "Daxil etdiyiniz məlumatlar",
        "summary_subtitle": "Bu, məlumat xülasəsidir. Diaqnostik nəticə deyil.",
        "summary_success": "Məlumatlar yoxlanıldı. Xülasəni aşağıda nəzərdən keçirin.",
        "summary_edit": "Düzəliş etmək üçün yuxarıdakı sahələri dəyişin və yenidən göndərin.",
        "not_provided": "Daxil edilməyib",
        "footer": "İnternetsiz OBD-II köməkçisi · Versiya 0.3",
        "fix_errors": "Davam etmək üçün aşağıdakı sahələri yoxlayın.",
        "required_manufacturer": "İstehsalçını daxil edin, məsələn, Toyota.",
        "required_model": "Avtomobilin modelini daxil edin, məsələn, Corolla.",
        "required_year": "Avtomobilin buraxılış ilini daxil edin.",
        "required_engine_type": "Mühərrik növünü seçin.",
        "required_symptoms": "Müşahidə etdiyiniz əlamətləri təsvir edin.",
        "invalid_manufacturer": "İstehsalçı adı ən çox 80 simvoldan ibarət ola bilər.",
        "invalid_model": "Model adı ən çox 80 simvoldan ibarət ola bilər.",
        "invalid_year": f"Buraxılış ilini {MIN_YEAR}–{MAX_YEAR} aralığında tam ədəd kimi daxil edin.",
        "invalid_engine_type": "Siyahıdan mühərrik növünü seçin.",
        "invalid_displacement": "Mühərrik həcmini 0-dan böyük, ən çox 100 litr daxil edin (məsələn, 1,6) və ya boş saxlayın.",
        "invalid_mileage": "Yürüşü sıfır və ya müsbət tam ədəd kimi daxil edin (məsələn, 85000) və ya boş saxlayın.",
        "invalid_symptoms": "Əlamətlərin təsviri 1–5000 simvoldan ibarət olmalıdır.",
        "invalid_obd_code": "OBD-II kodu sahəsinə ən çox 100 simvol daxil edin.",
    },
    "en": {
        "select_manufacturer": "Select or search manufacturer",
        "select_model": "Select or search model",
        "select_manufacturer_first": "Select a manufacturer first",
        "select_year": "Select model year",
        "not_listed": "Other / Not listed",
        "manual_manufacturer": "Enter manufacturer name",
        "manual_model_label": "Enter model name",
        "catalog_limit": "This catalog is not exhaustive; enter unlisted names manually. Selecting a year does not verify production years, engine specifications, or code compatibility.",
        "language": "Interface language",
        "eyebrow": "OFFLINE OBD-II ASSISTANT · V0.3",
        "hero_title": "Every detail matters.",
        "hero_description": "Enter your vehicle details. Review OBD-II code meanings, possible causes, and safe next steps.",
        "status": "10 local codes · Offline",
        "vehicle_title": "About your vehicle",
        "vehicle_subtitle": "Accurate details make for a clearer starting point.",
        "required_note": "Fields marked * are required.",
        "manufacturer": "Manufacturer", "manufacturer_placeholder": "For example, Toyota",
        "model": "Model", "model_placeholder": "For example, Corolla",
        "year": "Year", "year_placeholder": "For example, 2020",
        "engine_type": "Engine type", "engine_placeholder": "Select an engine type",
        "gasoline": "Gasoline", "diesel": "Diesel", "hybrid": "Hybrid", "electric": "Electric",
        "displacement": "Engine displacement",
        "displacement_label": "Engine displacement (L, optional)",
        "displacement_placeholder": "For example, 1.6",
        "mileage": "Mileage", "mileage_label": "Mileage (km, optional)",
        "mileage_placeholder": "For example, 85000",
        "symptoms_title": "What have you noticed?",
        "symptoms_subtitle": "Sounds, vibrations, warning lights, or changes in behavior.",
        "symptoms": "Symptom description",
        "symptoms_placeholder": "What is happening? When did it start? Under what conditions does it happen?",
        "symptoms_hint": "Include when the symptoms appear and the conditions you notice them in.",
        "obd_code": "OBD-II codes", "obd_label": "OBD-II diagnostic trouble codes (optional)",
        "obd_placeholder": "For example, P0301, P0171",
        "obd_hint": "Separate codes with commas. Only the 10 local codes are explained; symptom-only analysis is not supported yet.",
        "analyze": "Analyze Vehicle",
        "submit_hint": "The preliminary report uses local code references and fixed rules.",
        "guide_title": "A clear start in three steps",
        "step1_title": "Introduce your vehicle", "step1_body": "Add the essential vehicle details.",
        "step2_title": "Describe the symptoms", "step2_body": "Share your observations in your own words.",
        "step3_title": "Review the report", "step3_body": "Read the code explanations, safety notes, and limitations.",
        "scope_title": "About this version",
        "scope_body": "V0.3 uses a local code library. No generative AI is involved. Possible causes are not confirmed diagnoses.",
        "privacy_title": "In this browser session",
        "privacy_body": "Your information stays in this session. It is not written to a database or sent to an AI service.",
        "summary_title": "Your vehicle information",
        "summary_subtitle": "This is an information summary, not a diagnostic result.",
        "summary_success": "Information checked. Review your summary below.",
        "summary_edit": "To make a correction, edit the fields above and submit again.",
        "not_provided": "Not provided",
        "footer": "Offline OBD-II assistant · Version 0.3",
        "fix_errors": "Check the following fields to continue.",
        "required_manufacturer": "Enter the manufacturer, for example, Toyota.",
        "required_model": "Enter the vehicle model, for example, Corolla.",
        "required_year": "Enter the vehicle's model year.",
        "required_engine_type": "Select an engine type.",
        "required_symptoms": "Describe the symptoms you have noticed.",
        "invalid_manufacturer": "The manufacturer name must be 80 characters or fewer.",
        "invalid_model": "The model name must be 80 characters or fewer.",
        "invalid_year": f"Enter a whole-number year between {MIN_YEAR} and {MAX_YEAR}.",
        "invalid_engine_type": "Select an engine type from the list.",
        "invalid_displacement": "Enter a displacement greater than 0 and up to 100 liters (for example, 1.6), or leave it blank.",
        "invalid_mileage": "Enter mileage as zero or a positive whole number (for example, 85000), or leave it blank.",
        "invalid_symptoms": "The symptom description must contain 1–5000 characters.",
        "invalid_obd_code": "Enter no more than 100 characters in the OBD-II code field.",
    },
}


for language, report_text in REPORT_TEXT.items():
    TEXT[language].update(report_text)

for language, home_text in HOME_TEXT.items():
    TEXT[language].update(home_text)
    for key in ("eyebrow", "scope_body", "footer"):
        TEXT[language][key] = TEXT[language][key].replace("0.3", "0.7")
    TEXT[language].update(SYMPTOM_TEXT[language])
    TEXT[language]["obd_hint"] = (
        "Kodları vergüllə ayırın. Yalnız yerli bazadakı 10 kod izah olunur."
        if language == "az" else
        "Separate codes with commas. Only the 10 local codes are explained."
    )
    TEXT[language]["submit_hint"] = (
        "İlkin bələdçi yerli kod məlumatlarından və seçilmiş əlamətlərə aid sabit qaydalardan hazırlanır."
        if language == "az" else
        "Preliminary guidance uses local code references and fixed rules for selected symptoms."
    )
    TEXT[language]["scope_body"] = (
        "V0.7 yerli kod və əlamət qaydalarından istifadə edir. Generativ AI yoxdur; mümkün səbəblər diaqnoz deyil."
        if language == "az" else
        "V0.7 uses local code references and symptom rules. No generative AI; possible causes are not a diagnosis."
    )
    TEXT[language]["required_symptoms"] = (
        "Ən azı bir əlamət, təcili müşahidə, əlavə təsvir və ya OBD kodu daxil edin."
        if language == "az" else
        "Select a symptom or urgent observation, enter a description, or provide an OBD code."
    )
    TEXT[language]["invalid_symptom_selection"] = (
        "Əlamət seçimlərini yoxlayın."
        if language == "az" else "Check the symptom selections."
    )
    TEXT[language]["step2_body"] = (
        "Müşahidə etdiyiniz əlamətləri seçin; əlavə qeydlər istəyə bağlıdır."
        if language == "az" else "Select what you noticed; extra notes are optional."
    )
    TEXT[language]["footer"] = (
        "İnternetsiz avtomobil bələdçisi · Versiya 0.7"
        if language == "az" else "Offline vehicle guidance · Version 0.7"
    )


def translate(language: str, key: str) -> str:
    return TEXT[language][key]
