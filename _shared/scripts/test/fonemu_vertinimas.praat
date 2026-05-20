# Skaičiuoja fonemų koeficientus.
# Daroma prielaida, kad fonemos yra pirmajame TextGrid takelyje.
# Daroma prielaida, kad TextGrid ir wav failų pavadinimai sutampa.
# Kiekvienam textgrid failui rezultatus spausdina į atskirą failą rezultatų kataloge, kurio pavadinimas toks pat, kaip textgrid failo, tik pridedama atitinkama priesaga pagal skaičiuojamus koeficientus (pavyzdžiui, rezultatu_failo_priesaga_mfcc$) ir plėtinys rezultatu_failo_plėtinys$.

# v0.6 - jei buvo tarpas (buvo tuščių fonemų) tarp einamosios fonemos ir prieš tai apdorotos, 
#        spausdina tuščią eilutę, kad parodytų, jog koeficientai ne iš gretimų fonemų
# v0.5 - skaičiuodami koeficientus, išplėsime fonemą per time_shift į kairę ir į dešinę, 
#        kad atstumas tarp gretimų fonemų koeficientų langų centrų būtų lygus time_step
# v0.4 - pakeistas rezultatų išvedimas: 1 ženklas po kablelio
# v0.3 - pakeistas rezultatų išvedimas: rezultatai rašomi į buferį, o į failą rašomi kas buferio_dydis_mfcc ir buferio_dydis_bark fonemų
# v0.2 - pakeistas rezultatų išvedimas: po kadrą kiekvienoje eilutėje, 3 ženklai po kablelio, koeficientų skaičius failo pradžioje.
# v0.1 - pirma versija. 

##################### NAUDOTOJO PARAMETRAI: PRADŽIA ############################

# wav ir textgrid katalogai
# katalogus reikia nurodyti su baigiamuoju "\"
# rezultatų katalogas gali ir neegzistuoti, skriptas jį sukurs
wav_katalogas$ = ".\kiti\kiti12\wav\"
textgrid_katalogas$ = ".\final_B\TextGrid_fon_kiti12_lthmm_prec1_naujas_A\"
rezultatu_katalogas$ = ".\final_B\TextGrid_fon_kiti12_lthmm_prec1_naujas_A\"

wav_katalogas$ = "D:\Uni\Bachelors\CourseWork\wetransfer_easyalignsteps_4-praat_2026-03-09_1750\wav_TextGrid\wav\"
textgrid_katalogas$ = "D:\Uni\Bachelors\CourseWork\wetransfer_easyalignsteps_4-praat_2026-03-09_1750\wav_TextGrid\TextGrid\"
rezultatu_katalogas$ = "D:\Uni\Bachelors\CourseWork\wetransfer_easyalignsteps_4-praat_2026-03-09_1750\wav_TextGrid\VertinimoResults\"

# wav_katalogas$ = ".\LRMC\wav\"
# textgrid_katalogas$ = ".\LRMC\TextGrid_fon_LRMC_lthmm_prec0_naujas_A\"
# rezultatu_katalogas$ = ".\LRMC\TextGrid_fon_LRMC_lthmm_prec0_naujas_A\"

# ar rezultatus rašyti į vieną failą, ar į atskirus kiekvienam textgrid failui
vienas_rezultatu_failas = 1 ; 1 arba 0

# jei į vieną, koks turėtų būti failo pavadinimas (be priesagos ir be plėtinio)
rezultatu_failo_pav$ = "rez"

# failo, į kurį bus išvadami rezultatai, plėtinys (jis bus sukurtas rezultatų kataloge)
rezultatu_failo_plėtinys$ = ".txt"

# jei testas_fonemu_sk > 0, apskaičiuoja tik tiek kiekvieno nurodyto failo pirmųjų fonemų (skirta testavimui). 
# Priešingu atveju, skaičiuoja visas.
;testas_fonemu_sk = 13
testas_fonemu_sk = 0

# Pasirinkti, kuriuos koeficientus skaičiuoti. Gali būti "mfcc" ir "bark".
skaiciuojami_koeficientai$# = {"mfcc"} ; {"mfcc", "bark"} arba {"mfcc"} arba {"bark"}

############################
# bendri parametrai visiems koeficientams. Bus naudojami, jei atskiriems koeficientams nebus nurodytos kitokios reikšmės

# po kiek koeficientų matricų išsaugoti į failą vienu metu. Jei = 0, viską išsaugo per vieną kartą, pabaigoje
buferio_dydis = 20

# number of coefficients
koef_sk = 12
# window length (s)
lilg = 0.015
# time step (s)
time_step = 0.005; 0.005 arba 0.010

# Filter bank parameters:
# Position of first filter (mel)
position_of_first_filter = 100
# Distance between filters (mel)
distance_between_filters = position_of_first_filter
# Maximum frequency (mel)
maximum_frequency = 0

############################
# MFCC parametrai

rezultatu_failo_priesaga_mfcc$ = "_mfcc"

# po kiek koeficientų matricų išsaugoti į failą vienu metu. Jei = 0, viską išsaugo per vieną kartą, pabaigoje
buferio_dydis_mfcc = buferio_dydis

# number of coefficients
koef_sk_mfcc = koef_sk
# window length (s)
lilg_mfcc = lilg
# time step (s)
time_step_mfcc = time_step

# Filter bank parameters:
# Position of first filter (mel)
position_of_first_filter_mfcc = 100
# Distance between filters (mel)
distance_between_filters_mfcc = position_of_first_filter_mfcc
# Maximum frequency (mel)
maximum_frequency_mfcc = maximum_frequency

############################
# Bark spektro parametrai

rezultatu_failo_priesaga_bark$ = "_bark"

# po kiek koeficientų matricų išsaugoti į failą vienu metu. Jei = 0, viską išsaugo per vieną kartą, pabaigoje
buferio_dydis_bark = buferio_dydis

# number of coefficients
;koef_sk_bark = koef_sk
# window length (s)
lilg_bark = lilg
# time step (s)
time_step_bark = time_step

# Filter bank parameters:
# Position of first filter (bark)
position_of_first_filter_bark = 1.0
# Distance between filters (bark)
distance_between_filters_bark = position_of_first_filter_bark
# Maximum frequency (bark)
maximum_frequency_bark = maximum_frequency

##################### NAUDOTOJO PARAMETRAI: PABAIGA ############################

# Globalios konstantos

# takelių numeriai
phones_takelio_nr = 1

fonema_pauze$ = "_>"

textgrid_failo_pletinys$ = ".TextGrid"
wav_failo_pletinys$ = ".wav"

# Pradžia

writeInfoLine: "Pradžia ", date$()

skaiciuojami_koeficientai_sk = size (skaiciuojami_koeficientai$#)

createFolder: rezultatu_katalogas$

# atnaujiname rezultatų failus
if vienas_rezultatu_failas == 1
   @apibrezti_ir_trinti_rezultatu_failus: rezultatu_failo_pav$
   pirmas_mfcc = 1
   pirmas_bark = 1
endif

buferis_mfcc$ = ""
buferis_bark$ = ""
buferio_skaitliukas_mfcc = 0
buferio_skaitliukas_bark = 0

# skaičiuodami koeficientus, išplėsime fonemą per tiek į kairę ir į dešinę
time_shift = 0.01
if time_step == 0.005
   time_shift = 0.0125
endif

# įsimena paskutinę apdorotą fonamą, kad būtų galima patikrinti, ar 
# buvo tarpas (buvo tuščių fonemų) tarp einamosios fonemos ir prieš tai apdorotos (v0.6)
paskutine_fonema = 0

# gauname sąrašą TextGrid failų iš TextGrid failų katalogo
textgrid_failai$# = fileNames$# (textgrid_katalogas$ + "*" + textgrid_failo_pletinys$)
appendInfoLine: "Kataloge " + textgrid_katalogas$ + " surasta " + string$(size(textgrid_failai$#)) + " TextGrid failų."

for i to size(textgrid_failai$#)
   appendInfoLine: "Apdorosime failą ", textgrid_failai$#[i]
   textgrid_failas_be_pletinio$ = mid$(textgrid_failai$#[i], 1, length(textgrid_failai$#[i]) - length (textgrid_failo_pletinys$))
   if vienas_rezultatu_failas != 1
      rezultatu_failo_pav$ = textgrid_failas_be_pletinio$
   endif
   # jei atitinkamas failas egzistuoja ir wav failų kataloge
   wav_failas$ = wav_katalogas$ + textgrid_failas_be_pletinio$ + wav_failo_pletinys$
   if fileReadable (wav_failas$)
      # atnaujiname rezultatų failus
      if vienas_rezultatu_failas != 1
         @apibrezti_ir_trinti_rezultatu_failus: textgrid_failas_be_pletinio$
         pirmas_mfcc = 1
         pirmas_bark = 1
      endif
      @fonemu_koeficientu_skaiciavimas: textgrid_katalogas$ + textgrid_failai$#[i], wav_failas$, rezultatu_failas_mfcc$, rezultatu_failas_bark$
   else
      appendInfoLine: "Atitinkamas wav failas nerastas."
   endif
endfor

# ištuštiname buferius, jei rezultatai rašomi į bendrą failą
if vienas_rezultatu_failas == 1
   if buferio_skaitliukas_mfcc != 0
      appendFile (rezultatu_failas_mfcc$, buferis_mfcc$)
      buferis_mfcc$ = ""
      buferio_skaitliukas_mfcc = 0
   endif
   if buferio_skaitliukas_bark != 0
      appendFile (rezultatu_failas_bark$, buferis_bark$)
      buferis_bark$ = ""
      buferio_skaitliukas_bark = 0
   endif
endif

appendInfoLine: "Pabaiga ", date$()

############################################################################
# Pagrindinė procedūra.
############################################################################

procedure fonemu_koeficientu_skaiciavimas: .textgrid_failas$, .wav_failas$, .rezultatu_failas_mfcc$, .rezultatu_failas_bark$

   # Pradedame skaičiavimą

   .textgrid = Read from file: .textgrid_failas$
   .wav = Read from file: .wav_failas$
   end_time = Get end time
   
   selectObject: .textgrid
   if testas_fonemu_sk > 0
      intsk = testas_fonemu_sk
   else
      intsk = Get number of intervals... phones_takelio_nr
   endif

   # kiekvienai netuščiai fonemai darome
   for fon_nr from 1 to intsk
      selectObject: .textgrid
      lab1$ = Get label of interval... phones_takelio_nr fon_nr
      if lab1$ != "" and lab1$ != "_" and lab1$ != fonema_pauze$

         pra = Get start point... phones_takelio_nr fon_nr
         pab = Get end point... phones_takelio_nr fon_nr
         # skaičiuodami koeficientus, išplėsime fonemą per time_shift į kairę ir į dešinę
         pra -= time_shift
         pab += time_shift
         #pab = pra + lilg*2+0.0001

         # kad būtų galima paskaičiuoti koeficientus, intervalo ilgis turi būti bent lilg*2+0.0001
         if pab - pra < lilg*2+0.0001
            # per trumpas intervalas. Perskaičiuojame pra ir pab principu: [pradzia – epsilon, pabaiga + epsilon]
            fon_ilg = pab - pra
            epsilon = (lilg*2+0.0001 - fon_ilg)/2
            pra = pra - epsilon
            pab = pab + epsilon
         endif
         
         if pra < 0
            pab -= pra
            pra = 0
         endif
         
         if pab > end_time
            pra -= pab - end_time
            pab = end_time
         endif

         selectObject: .wav
         .wav_part = Extract part: pra, pab, "rectangular", 1.0, "no"

         # skaičiuojame koeficientus
         
         for .skaiciuojami_koeficientai_nr to skaiciuojami_koeficientai_sk
            .skaiciuojami_koeficientai$ = skaiciuojami_koeficientai$#[.skaiciuojami_koeficientai_nr]

            if .skaiciuojami_koeficientai$ == "mfcc"
               selectObject: .wav_part
               .t1 = noprogress To MFCC: koef_sk_mfcc, lilg_mfcc, time_step_mfcc, position_of_first_filter_mfcc, distance_between_filters_mfcc, maximum_frequency_mfcc
               .matrix = noprogress To Matrix

               if pirmas_mfcc
                  .nb_rows = Get number of rows
                  appendFileLine (.rezultatu_failas_mfcc$, .nb_rows)
                  pirmas_mfcc = 0
               else
                  # jei buvo tarpas (buvo tuščių fonemų) tarp šios fonemos ir prieš tai apdorotos, 
                  # spausdiname tuščią eilutę, kad parodytume, jog koeficientai ne iš gretimų fonemų
                  if fon_nr != paskutine_fonema + 1
                     buferis_mfcc$ += newline$
                  endif
               endif
               paskutine_fonema = fon_nr

               @rasyti_koef_i_buferi_is_matricos: buferis_mfcc$, .matrix, lab1$
               buferis_mfcc$ = rasyti_koef_i_buferi_is_matricos.buferis$
               buferio_skaitliukas_mfcc += 1
               if buferio_dydis_mfcc > 0 and buferio_skaitliukas_mfcc mod buferio_dydis_mfcc == 0
                  appendFile (.rezultatu_failas_mfcc$, buferis_mfcc$)
                  buferis_mfcc$ = ""
                  buferio_skaitliukas_mfcc = 0
               endif
               removeObject (.matrix, .t1)
            elsif .skaiciuojami_koeficientai$ == "bark"
               selectObject: .wav_part
               .t1 = noprogress To BarkSpectrogram: lilg_bark, time_step_bark, position_of_first_filter_bark, distance_between_filters_bark, maximum_frequency_bark
               .matrix = noprogress To Matrix: 1
               if pirmas_bark
                  .nb_rows = Get number of rows
                  appendFileLine (.rezultatu_failas_bark$, .nb_rows)
                  pirmas_bark = 0
               endif
               @rasyti_koef_i_buferi_is_matricos: buferis_bark$, .matrix, lab1$
               buferis_bark$ = rasyti_koef_i_buferi_is_matricos.buferis$
               buferio_skaitliukas_bark += 1
               if buferio_dydis_bark > 0 and buferio_skaitliukas_bark mod buferio_dydis_bark == 0
                  appendFile (.rezultatu_failas_bark$, buferis_bark$)
                  buferis_bark$ = ""
                  buferio_skaitliukas_bark = 0
               endif
               removeObject (.matrix, .t1)
            else
               appendInfoLine: "Koeficientai ", .skaiciuojami_koeficientai$, " nežinomi."
            endif
         endfor
         
         removeObject (.wav_part)
      endif
   endfor

   # ištuštiname buferius, jei rezultatai rašomi į atskirus failus
   if vienas_rezultatu_failas != 1
      if buferio_skaitliukas_mfcc != 0
         appendFile (.rezultatu_failas_mfcc$, buferis_mfcc$)
         buferis_mfcc$ = ""
         buferio_skaitliukas_mfcc = 0
      endif
      if buferio_skaitliukas_bark != 0
         appendFile (.rezultatu_failas_bark$, buferis_bark$)
         buferis_bark$ = ""
         buferio_skaitliukas_bark = 0
      endif
   endif
   
   # pašaliname sukurtus objektus   
   removeObject (.textgrid, .wav)
endproc

############################################################################
# Surašo į vieną failo eilutę paduotą parametrą .lab1$ (garso pavadinimą), 
# matricos eilučių skaičių (koeficientų skaičių), matricos stulpelių skaičių (kadrų skaičių) ir visus koeficientus iš Matrix .matrix
# stulpeliais (pirmiausia visus elementus iš pirmo stulpelio, tada iš antro ir t.t.)
############################################################################

procedure rasyti_koef_i_buferi_is_matricos (.buferis$, .matrix, .lab1$)
   select .matrix
   .nb_rows = Get number of rows
   .nb_col = Get number of columns

   for .j from 1 to .nb_col
      .eilute$ = .lab1$ + " "
      for .k from 1 to .nb_rows
         .koef = Get value in cell... .k .j
         .eilute$ = .eilute$ + " " + fixed$ (.koef, 1)
      endfor
      .buferis$ += .eilute$ + newline$
   endfor

endproc

############################################################################
# apibrezti_ir_trinti_rezultatu_failus
############################################################################

procedure apibrezti_ir_trinti_rezultatu_failus: .rezultatu_failo_pav$
   rezultatu_failas_mfcc$ = rezultatu_katalogas$ + .rezultatu_failo_pav$ + rezultatu_failo_priesaga_mfcc$ + rezultatu_failo_plėtinys$
   rezultatu_failas_bark$ = rezultatu_katalogas$ + .rezultatu_failo_pav$ + rezultatu_failo_priesaga_bark$ + rezultatu_failo_plėtinys$
   for .skaiciuojami_koeficientai_nr to skaiciuojami_koeficientai_sk
      .skaiciuojami_koeficientai$ = skaiciuojami_koeficientai$#[.skaiciuojami_koeficientai_nr]
      if .skaiciuojami_koeficientai$ == "mfcc"
         deleteFile: rezultatu_failas_mfcc$
      elsif .skaiciuojami_koeficientai$ == "bark"
         deleteFile: rezultatu_failas_bark$
      endif
   endfor
endproc