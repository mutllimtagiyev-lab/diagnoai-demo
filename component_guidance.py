"""Curated inspection candidates, never confirmed defects or replacement advice."""

COPY = {
 'en': {'title':'Components for professional inspection', 'status':'Confirmed faults: none. All inputs are owner reports; component candidates remain unconfirmed.', 'why':'Why relevant', 'checks':'Checks to request', 'missing':'More information needed', 'light':'Engine warning light', 'unknown':'Unknown / not checked', 'off':'Off', 'steady':'Steady', 'flashing':'Flashing', 'hybrid':'Hybrid combustion-engine type is unverified. Confirm fuel type and whether symptoms occur with the combustion engine running before applying engine-component guidance.', 'empty':'No supported component pattern for these selections. Use the system guidance and seek professional assessment.', 'condition':'Reported condition influencing inspection', 'cold_start':'Ask the technician to compare cold-start temperature readings with ambient conditions.', 'warm_engine':'Ask the technician to review operating-temperature data when evaluating the complaint.', 'acceleration':'Reported acceleration-related power loss makes load-related air and fuel data relevant; do not reproduce it yourself.', 'idling':'Reported idle symptoms make idle air control and fuel correction data relevant.', 'continuous':'A continuous complaint helps the technician plan inspection; it does not establish severity.', 'braking':'A braking-related complaint requires a professional control and brake assessment.', 'ask':'Clarify cold versus warm operation, whether power loss occurs during acceleration, and whether it is intermittent or constant.'},
 'az': {'title':'Peşəkar yoxlama üçün hissələr', 'status':'Təsdiqlənmiş nasazlıq: yoxdur. Bütün girişlər sahibin müşahidələridir; hissələrə aid ehtimallar təsdiqlənməyib.', 'why':'Niyə əlaqəli ola bilər', 'checks':'Ustadan istəniləcək yoxlamalar', 'missing':'Əlavə məlumat lazımdır', 'light':'Mühərrik xəbərdarlıq işığı', 'unknown':'Bilinmir / yoxlanmayıb', 'off':'Sönük', 'steady':'Daimi yanır', 'flashing':'Yanıb-sönür', 'hybrid':'Hibridin daxili yanma mühərrikinin yanacaq növü təsdiqlənməyib. Mühərrik hissələri üzrə bələdçidən əvvəl yanacaq növünü və əlamətin mühərrik işləyərkən yaranmasını dəqiqləşdirin.', 'empty':'Bu seçimlər üçün dəstəklənən hissə nümunəsi yoxdur. Sistem bələdçisinə baxın və peşəkar yoxlama alın.', 'condition':'Yoxlamaya təsir edən bildirilmiş şərait', 'cold_start':'Ustadan soyuq işə salmada temperatur göstəricilərini ətraf mühitlə müqayisə etməsini istəyin.', 'warm_engine':'Ustadan şikayəti qiymətləndirərkən iş temperaturu məlumatına baxmasını istəyin.', 'acceleration':'Sürətlənmədə güc itkisi yükə aid hava və yanacaq məlumatını əlaqəli edir; özünüz təkrarlamayın.', 'idling':'Boş rejim əlamətləri boş rejim hava idarəetməsi və yanacaq korreksiyası məlumatını əlaqəli edir.', 'continuous':'Davamlı şikayət ustaya yoxlamanı planlamaqda kömək edir; ciddiliyi təsdiqləmir.', 'braking':'Əyləcləmə ilə əlaqəli şikayət peşəkar idarəetmə və əyləc yoxlaması tələb edir.', 'ask':'Soyuq və ya isti rejimi, güc itkisinin sürətlənmədə yaranmasını və fasiləli və ya davamlı olmasını dəqiqləşdirin.'}
}

# Each entry: stable ID, applicable engines, names, rationale, professional check.
COMPONENTS = (
 ('ignition', ('gasoline',), ('Spark plugs and ignition coils','Alışdırma şamları və bobinlər'), ('Uneven ignition can contribute to rough idle or power loss.','Qeyri-bərabər alışdırma titrəmə və güc itkisinə səbəb ola bilər.'), ('Review misfire data and ignition condition using the correct service procedure.','Düzgün servis proseduru ilə yanma pozuntusu məlumatını və alışdırmanı yoxlamaq.')),
 ('injection', ('gasoline','diesel'), ('Fuel injectors and delivery system','Yanacaq injektorları və təchizat sistemi'), ('Uneven fuel delivery can affect combustion and power.','Qeyri-bərabər yanacaq təchizatı yanmaya və gücə təsir edə bilər.'), ('Request vehicle-specific fuel-delivery and injector assessment by a qualified technician.','İxtisaslı ustadan avtomobilə uyğun yanacaq təchizatı və injektor yoxlaması istəmək.')),
 ('air', ('gasoline','diesel'), ('Air intake, hoses and relevant engine sensors','Hava girişi, şlanqlar və uyğun mühərrik sensorları'), ('Air supply and measured engine conditions influence fuel control.','Hava təchizatı və ölçülən mühərrik şəraiti yanacaq idarəetməsinə təsir edir.'), ('Review intake integrity and sensor plausibility; check vacuum systems only where fitted.','Hava girişinin bütövlüyünü və sensor göstəricilərinin uyğunluğunu, varsa vakuum sistemini yoxlamaq.')),
 ('mechanical', ('gasoline','diesel'), ('Mechanical engine condition','Mühərrikin mexaniki vəziyyəti'), ('Uneven cylinder operation can have mechanical causes as well.','Silindrlərin qeyri-bərabər işi mexaniki səbəblərlə də bağlı ola bilər.'), ('If preliminary data warrants it, request a professional cylinder-condition assessment.','İlkin məlumat əsas verirsə, peşəkar silindr vəziyyəti yoxlaması istəmək.')),
)

def component_candidates(vehicle):
    if not set(vehicle.symptom_ids).intersection(('rough_idle','power_loss')):
        return ()
    return tuple(row for row in COMPONENTS if vehicle.engine_type in row[1])

def render_components(vehicle, language):
    import streamlit as st
    c = COPY[language]
    index = 0 if language == 'en' else 1
    st.subheader(c['title'])
    st.info(c['status'])
    candidates = component_candidates(vehicle)
    if vehicle.engine_type == 'hybrid':
        st.info(c['hybrid'])
    if not candidates:
        st.caption(c['empty'])
    for row in candidates:
        with st.container(border=True):
            st.markdown('#### ' + row[2][index])
            st.markdown('**' + c['why'] + '**')
            st.write(row[3][index])
            st.markdown('**' + c['checks'] + '**')
            st.write(row[4][index])
    st.write(c['light'] + ': ' + c[vehicle.warning_light])
    if vehicle.issue_condition and candidates:
        st.markdown('**' + c['condition'] + '**')
        st.write(c[vehicle.issue_condition])
    else:
        st.markdown('**' + c['missing'] + '**')
        st.write(c['ask'])
