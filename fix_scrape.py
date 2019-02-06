# -*- coding: utf-8 -*-


import gzip
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from bs4.diagnose import diagnose
import logging
import json
import glob, os
import re
from dateutil import parser


DATADIR = "data/{}"

REPARSE_SAVE_DIR = "visir_slurper/data_reparse"

authors = ["Kristján Már Unnarsson",
"Lillý Valgerður Pétursdóttir",
"Lóa Pind Aldísardóttir",
"Magnús Guðmundsson",
"Magnús Hlynur Hreiðarsson",
"Margrét Erla Maack",
"Nadine Guðrún Yaghi",
"Nanna Elísa Jakobsdóttir",
"Óli Kristján Ármannsson",
"Ólöf Skaftadóttir",
"Óskar Ófeigur Jónsson",
"Pjetur Sigurðsson",
"Ragnheiður Tryggvadóttir",
"Rikka",
"Ritstjórn",
"Samúel Karl Ólason",
"Sindri Sindrason",
"Snærós Sindradóttir",
"Starri Freyr Jónsson",
"Stefán Árni Pálsson",
"Stefán Ó. Jónsson",
"Stefán Rafn Sigurbjörnsson",
"Sunna Karen Sigurþórsdóttir",
"Sunna Kristín Hilmarsdóttir",
"Svavar Hávarðsson",
"Sveinn Arnarsson",
"Sæunn Gísladóttir",
"Telma Tómasson",
"Tinni Sveinsson",
"Tryggvi Páll Tryggvason",
"Una Sighvatsdóttir",
"Viktoría Hermannsdóttir",
"unknown",
"Þorbjörn Þórðarson",
"Þórdís Valsdóttir",
"Þórgnýr Einar Albertsson",
"Þórhildur Þorkelsdóttir"]

DUPLICATES = ["data/unknown/Alvarlega slasaður eftir bílveltu.1.json",
"data/unknown/Alþingi Íslendinga sett.1.json",
"data/unknown/Alþingi kemur saman í dag.1.json",
"data/unknown/Alþjóðasamfélagið hefur brugðist.1.json",
"data/unknown/Annasamt hjá björgunarsveitum.1.json",
"data/unknown/Atvinnuleysi stendur í stað.1.json",
"data/unknown/Aðstoðuðu vélarvana bát.1.json",
"data/unknown/Á batavegi eftir bílveltu.1.json",
"data/unknown/Á gjörgæslu eftir bílveltu.1.json",
"data/unknown/Áfram í gæsluvarðhaldi.1.json",
"data/unknown/Ákærður fyrir manndráp.1.json",
"data/unknown/Árekstur á Reykjanesbraut.1.json",
"data/unknown/Banaslys á Ólafsfjarðarvegi.1.json",
"data/unknown/Banaslys á Suðurlandsvegi.1.json",
"data/unknown/Banaslys í Norðurárdal.1.json",
"data/unknown/Banaslys í Skagafirði.1.json",
"data/unknown/Beltin björguðu.1.json",
"data/unknown/Bensín hækkar.1.json",
"data/unknown/Bensínverð hækkar.1.json",
"data/unknown/Bensínverð lækkar.1.json",
"data/unknown/Bílbeltin björguðu.1.json",
"data/unknown/Bílvelta á Akureyri.1.json",
"data/unknown/Bílvelta á Grindavíkurvegi.1.json",
"data/unknown/Bílvelta á Hellisheiði.1.json",
"data/unknown/Bílvelta á Vesturlandsvegi.1.json",
"data/unknown/Bílvelta í Heiðmörk.1.json",
"data/unknown/Bílvelta í Kömbunum.1.json",
"data/unknown/Bílvelta í Þrengslunum.1.json",
"data/unknown/Bílvelta við Litlu kaffistofuna.1.json",
"data/unknown/Blóðtaka hjá Al-Qaeda.1.json",
"data/unknown/Brennuvargar á ferð í nótt.1.json",
"data/unknown/Breskir hermenn ákærðir fyrir morð.1.json",
"data/unknown/Breyttur útivistartími.1.json",
"data/unknown/Brotist inn í tvo söluturna.1.json",
"data/unknown/Brotist inn um hábjartan dag.1.json",
"data/unknown/Búinn að fá nóg.1.json",
"data/unknown/Búist við mikilli umferð við kirkjugarða.1.json",
"data/unknown/Búist við stormi í nótt.1.json",
"data/unknown/Búið að slökkva eldinn.1.json",
"data/unknown/Dagur íslenskrar tungu í dag.1.json",
"data/unknown/Discovery lenti heilu og höldnu.1.json",
"data/unknown/Dópsali handtekinn.1.json",
"data/unknown/Drengurinn kominn í leitirnar.1.json",
"data/unknown/Drengurinn látinn.1.json",
"data/unknown/Dæmdir fyrir líkamsárás á Selfossi.1.json",
"data/unknown/Dæmdur fyrir líkamsárás.1.json",
"data/unknown/Dæmdur í árs fangelsi.1.json",
"data/unknown/Dæmdur í lífstíðarfangelsi.1.json",
"data/unknown/Dæmdur í þriggja ára fangelsi.1.json",
"data/unknown/Einn á slysadeild eftir árekstur.1.json",
"data/unknown/Einn fluttur á slysadeild eftir árekstur.1.json",
"data/unknown/Einn með allar tölur réttar.1.json",
"data/unknown/Einn með allar tölurnar réttar.1.json",
"data/unknown/Ekið á dreng á reiðhjóli.1.json",
"data/unknown/Ekið á gangandi vegfaranda.1.json",
"data/unknown/Ekið á gangandi vegfarenda.1.json",
"data/unknown/Ekið á hjólreiðamann.1.json",
"data/unknown/Ekið á litla stúlku.1.json",
"data/unknown/Ekið á stúlku við Hólabrekkuskóla.1.json",
"data/unknown/Ekið á ungan dreng.1.json",
"data/unknown/Eldgosið í rénun.1.json",
"data/unknown/Eldsvoði í París.1.json",
"data/unknown/Eldur á Akureyri.1.json",
"data/unknown/Eldur í bíl á Akureyri.1.json",
"data/unknown/Eldur í bíl.1.json",
"data/unknown/Eldur í bílskúr.1.json",
"data/unknown/Eldur í blaðagámi.1.json",
"data/unknown/Eldur í Breiðholti.1.json",
"data/unknown/Eldur í fjölbýlishúsi í Breiðholti.1.json",
"data/unknown/Eldur í fjölbýlishúsi í Kópavogi.1.json",
"data/unknown/Eldur í fjölbýlishúsi.1.json",
"data/unknown/Eldur í Hafnarfirði.1.json",
"data/unknown/Eldur í potti.1.json",
"data/unknown/Eldur í ruslageymslu fjölbýlishúss.1.json",
"data/unknown/Eldur í ruslatunnu.1.json",
"data/unknown/Eldur í uppþvottavél.1.json",
"data/unknown/Ellefu fengu fálkaorðuna.1.json",
"data/unknown/Elsta kona heims látin.1.json",
"data/unknown/Endeavour á leið til jarðar.1.json",
"data/unknown/Engin gereyðingarvopn.1.json",
"data/unknown/Enginn með allar réttar í lottóinu.1.json",
"data/unknown/Enginn með allar tölur réttar.1.json",
"data/unknown/Enn ein kannabisræktunin stöðvuð.1.json",
"data/unknown/Enn haldið sofandi í öndunarvél.1.json",
"data/unknown/Enn í lífshættu.1.json",
"data/unknown/Erill hjá lögreglu í nótt.1.json",
"data/unknown/Erill hjá lögreglu.1.json",
"data/unknown/Erill hjá lögreglunni í nótt.1.json",
"data/unknown/ESSO hækkar bensínverð.1.json",
"data/unknown/ESSO hækkar bensínverðið.1.json",
"data/unknown/ETA sprengir á spáni.1.json",
"data/unknown/Fannst látinn.1.json",
"data/unknown/Fáir bátar á sjó.1.json",
"data/unknown/Festist undir brú.1.json",
"data/unknown/Feðgarnir fundnir heilir á húfi.1.json",
"data/unknown/Fíkniefnasalar handteknir.1.json",
"data/unknown/Fíkniefni fundust við húsleit í Kópavogi.1.json",
"data/unknown/Fjórir fluttir á slysadeild.1.json",
"data/unknown/Fjórtán stútar teknir um helgina.1.json",
"data/unknown/Fjögur umferðaróhöpp á Vestfjörðum.1.json",
"data/unknown/Fjögurra bíla árekstur á Miklubraut.1.json",
"data/unknown/Fjölmargar vísbendingar borist.1.json",
"data/unknown/Flest skíðasvæði landsins opin.1.json",
"data/unknown/Flóðbylgjuviðvörun dregin til baka.1.json",
"data/unknown/Flugslysaæfing í Vestmannaeyjum.1.json",
"data/unknown/Forsetakosningar í Mexíkó.1.json",
"data/unknown/Forskot Fréttablaðsins eykst.1.json",
"data/unknown/Forsætisráðherrann sagði af sér.1.json",
"data/unknown/Fórnarlamba minnst.1.json",
"data/unknown/Fyrsta barn ársins.1.json",
"data/unknown/Fyrsta útskriftin.1.json",
"data/unknown/Fyrsti vinningur gekk ekki út.1.json",
"data/unknown/Fyrstu kappræðurnar í kvöld.1.json",
"data/unknown/Geir vildi ná í Brown en fékk ekki samband.json",
"data/unknown/Gleðilegt nýtt ár!.1.json",
"data/unknown/Gleðilegt nýtt ár.1.json",
"data/unknown/Gömul frétt í Kastljósi.json",
"data/unknown/Gráösp valin tré ársins.1.json",
"data/unknown/Grásleppuvertíðin hafin.1.json",
"data/unknown/Grunur um íkveikju.1.json",
"data/unknown/Grunur um salmonellu í kjúklingum.1.json",
"data/unknown/Gunnar Rúnar áfram í gæsluvarðhaldi.1.json",
"data/unknown/Gæsluvarðhald rennur út í dag.1.json",
"data/unknown/Haldið sofandi í öndunarvél eftir bílslys.1.json",
"data/unknown/Haldið sofandi í öndunarvél.1.json",
"data/unknown/Harður árekstur á Akureyri.1.json",
"data/unknown/Harður árekstur á Breiðholtsbraut.1.json",
"data/unknown/Harður árekstur á Hringbraut.1.json",
"data/unknown/Harður árekstur á Miklubraut.1.json",
"data/unknown/Harður árekstur á Reykjanesbraut.1.json",
"data/unknown/Harður árekstur í Hafnarfirði.1.json",
"data/unknown/Harður jarðskjálfti í Japan.1.json",
"data/unknown/Hálka á Hellisheiði.1.json",
"data/unknown/Hálka á Holtavörðuheiði.1.json",
"data/unknown/Hálka víða um land.1.json",
"data/unknown/Hálkublettir á Hellisheiði.1.json",
"data/unknown/Heitavatnslaust á Akranesi.1.json",
"data/unknown/Heitavatnslaust í Árbæ.1.json",
"data/unknown/Heitavatnslaust í Grafarvogi.1.json",
"data/unknown/Herinn skaut á mótmælendur.1.json",
"data/unknown/Herjólfi seinkar.1.json",
"data/unknown/Herjólfur fer ekki fleiri ferðir í dag.1.json",
"data/unknown/Herjólfur siglir til Þorlákshafnar.1.json",
"data/unknown/Hjólaði í veg fyrir bíl.1.json",
"data/unknown/Hlaupið í rénun.1.json",
"data/unknown/Hraðakstur í Hvalfjarðargöngum.1.json",
"data/unknown/Hundruð þúsunda á flótta.1.json",
"data/unknown/Hundruð þúsunda mótmæltu.1.json",
"data/unknown/Hungursneyð í Afríku.1.json",
"data/unknown/Hvalfjarðargöng lokuð næstu nætur.1.json",
"data/unknown/Hvalveiðar við Ísland - Umræða á Alþingi.json",
"data/unknown/Hæstiréttur staðfesti gæsluvarðhald.1.json",
"data/unknown/Hæstiréttur staðfesti gæsluvarðhaldsúrskurð.1.json",
"data/unknown/Hæstiréttur staðfestir gæsluvarðhald.1.json",
"data/unknown/Icesave afgreitt úr fjárlaganefnd.1.json",
"data/unknown/Innbrot á Akureyri.1.json",
"data/unknown/Innbrot í sumarbústað í Grímsnesi.1.json",
"data/unknown/Innbrotahrina á höfuðborgarsvæðinu.1.json",
"data/unknown/Innbrotsþjófur gripinn glóðvolgur.1.json",
"data/unknown/Innbrotsþjófur í gæsluvarðhald.1.json",
"data/unknown/Íslenska ríkið sýknað.1.json",
"data/unknown/Íþróttir 13:00 - 31.05.2006.json",
"data/unknown/Jarðskjálftahrina á Reykjaneshrygg.1.json",
"data/unknown/Jarðskjálftahrina nærri Grímsey.1.json",
"data/unknown/Jarðskjálftahrina við Grímsey.1.json",
"data/unknown/Jarðskjálftar við Grímsey.1.json",
"data/unknown/Jarðskjálfti á Indónesíu.1.json",
"data/unknown/Jarðskjálfti í Chile.1.json",
"data/unknown/Jarðskjálfti í Indónesíu.1.json",
"data/unknown/Jarðskjálfti í Japan.1.json",
"data/unknown/Jarðskjálfti í Panama.1.json",
"data/unknown/Jarðskjálfti í Vatnajökli.1.json",
"data/unknown/Jólabasar Hringsins í dag.1.json",
"data/unknown/Kannabisræktun stöðvuð.1.json",
"data/unknown/Karlmaður stunginn í nótt.1.json",
"data/unknown/Kjarasamningar í uppnámi.1.json",
"data/unknown/Kjörfundur hefst í Páfagarði.1.json",
"data/unknown/Konan komin í leitirnar.1.json",
"data/unknown/Landssamtök Landeigenda á Íslandi stofnuð.1.json",
"data/unknown/Leit afturkölluð.1.json",
"data/unknown/Leiðrétting.1.json",
"data/unknown/Lenti heilu og höldnu.1.json",
"data/unknown/Lestarslys á Indlandi.1.json",
"data/unknown/Lést af slysförum.1.json",
"data/unknown/Lést í bílslysi.1.json",
"data/unknown/Lést í umferðarslysi.1.json",
"data/unknown/Lést í vélhjólaslysi.1.json",
"data/unknown/Lést í vinnuslysi.1.json",
"data/unknown/Lindsay Lohan aftur á leið í fangelsi.1.json",
"data/unknown/Líkamsárás í heimahúsi.1.json",
"data/unknown/Líkamsárás í Vestmannaeyjum.1.json",
"data/unknown/Líðan mannsins óbreytt.1.json",
"data/unknown/Ljósin tendruð á Oslóartrénu.1.json",
"data/unknown/Ljósleiðari fór í sundur.1.json",
"data/unknown/Lögreglan lýsir eftir Ingólfi Snæ.1.json",
"data/unknown/Lögreglan lýsir eftir stúlku.1.json",
"data/unknown/Lýst eftir 14 ára pilti.1.json",
"data/unknown/Lýst eftir 14 ára stúlku.1.json",
"data/unknown/Lýst eftir 15 ára stúlku.1.json",
"data/unknown/Lýst eftir 16 ára stúlku.1.json",
"data/unknown/Mannskæðar árásir í Bagdad.1.json",
"data/unknown/Mannskæðar árásir í Írak.1.json",
"data/unknown/Mannskæðar sprengjuárásir í Írak.1.json",
"data/unknown/Maðurinn látinn.1.json",
"data/unknown/Maðurinn sem lést.1.json",
"data/unknown/Meintir fíkniefnasmyglarar áfram í gæsluvarðhaldi.1.json",
"data/unknown/Meirihlutaviðræður hafnar í Kópavogi.1.json",
"data/unknown/Meirihlutinn í Grindavík sprunginn.1.json",
"data/unknown/Mikil svörun við kvörtunum Sigmundar.json",
"data/unknown/Mikill erill hjá lögreglu.1.json",
"data/unknown/Mikið fannfergi í Japan.1.json",
"data/unknown/Mikið um sjúkraflutninga í nótt.1.json",
"data/unknown/Mótmælt á Austurvelli í dag.1.json",
"data/unknown/Nafn konunnar sem lést.1.json",
"data/unknown/Nafn mannsins sem lést.1.json",
"data/unknown/Nafn stúlkunnar sem lést.1.json",
"data/unknown/Neville gætu þurft á aðgerð að halda.json",
"data/unknown/Nóg að gera hjá lögreglu.1.json",
"data/unknown/Nýr seðlabankastjóri í Bandaríkjunum.1.json",
"data/unknown/Nýtt leiðakerfi Strætó.1.json",
"data/unknown/Ofbeldismaður áfram í haldi.1.json",
"data/unknown/Opið á flestum skíðasvæðum.1.json",
"data/unknown/Opið á skíðasvæðum.1.json",
"data/unknown/Opið í Bláfjöllum í dag.1.json",
"data/unknown/Opið í Bláfjöllum og Skálafelli.1.json",
"data/unknown/Opið í Bláfjöllum.1.json",
"data/unknown/Opið í Hlíðarfjalli í dag.1.json",
"data/unknown/Opið í Hlíðarfjalli.1.json",
"data/unknown/Opnunartími Læknavaktarinnar yfir hátíðirnar.1.json",
"data/unknown/Ók á 153 kílómetra hraða.1.json",
"data/unknown/Ók á ljósastaur.1.json",
"data/unknown/Ók á staur á Akureyri.1.json",
"data/unknown/Ók á tæplega 200 kílómetra hraða.1.json",
"data/unknown/Ók undir áhrifum á ljósastaur.1.json",
"data/unknown/Óku inn í snjóflóð.1.json",
"data/unknown/Óttast þjóðarmorð.1.json",
"data/unknown/Óvenju mikið um sjúkraflutninga.1.json",
"data/unknown/Óveður á Kjalarnesi.1.json",
"data/unknown/Óveður á Vestfjörðum.1.json",
"data/unknown/Öflugur jarðskjálfti í Indónesíu.1.json",
"data/unknown/Öflugur jarðskjálfti í Íran.1.json",
"data/unknown/Öflugur jarðskjálfti í Japan.1.json",
"data/unknown/Ökumaður slapp ómeiddur úr bílveltu.1.json",
"data/unknown/Ölvaður ökumaður í árekstri.1.json",
"data/unknown/Ölvaður ökumaður reyndi að stinga lögregluna af.1.json",
"data/unknown/Ölvaður ökumaður velti bíl.1.json",
"data/unknown/Örtröð í ríkinu.1.json",
"data/unknown/Pilturinn kominn í leitirnar.1.json",
"data/unknown/Pottur gleymdist á eldavél.1.json",
"data/unknown/Punxsutawney Phil sá ekki skuggann sinn.1.json",
"data/unknown/Pústrar í Vestmannaeyjum.1.json",
"data/unknown/Raflögnum og rafbúnaði víða ábótavant.1.json",
"data/unknown/Rafmagn komið á að nýju.1.json",
"data/unknown/Rafmagn komið á á Akranesi.1.json",
"data/unknown/Rafmagn komið á.1.json",
"data/unknown/Rafmagnslaust á Akranesi.1.json",
"data/unknown/Rafmagnslaust í Fossvogi.1.json",
"data/unknown/Rafmagnslaust í Mosfellsbæ.1.json",
"data/unknown/Rafmagnslaust víða í Reykjavík.1.json",
"data/unknown/Rafmagnstruflanir á Vesturlandi.1.json",
"data/unknown/Rannsókn á lokastigi.1.json",
"data/unknown/Rannsóknin langt komin.1.json",
"data/unknown/Reykvísk börn fá frístundakort.1.json",
"data/unknown/Réttindalaus ökumaður stöðvaður.1.json",
"data/unknown/Ríkisráð kemur saman.1.json",
"data/unknown/Róleg nótt hjá lögreglu.1.json",
"data/unknown/Rússar banna reykingar.1.json",
"data/unknown/Ræningjarnir enn ófundnir.1.json",
"data/unknown/Samkomulag á síðustu stundu.1.json",
"data/unknown/Samningar í höfn.1.json",
"data/unknown/Sextán daga átak gegn kynbundnu ofbeldi.1.json",
"data/unknown/Sharapova stynur of hátt.json",
"data/unknown/Síbrotamaður í 18 mánaða fangelsi.1.json",
"data/unknown/Síbrotamaður í gæsluvarðhald.1.json",
"data/unknown/Síbrotamaður tekinn úr umferð.1.json",
"data/unknown/Síðasti gyðingurinn í Afganistan.1.json",
"data/unknown/Sjómaður hætt kominn.1.json",
"data/unknown/Skáksveit Rimaskóla Norðurlandameistari.1.json",
"data/unknown/Skíðasvæði opin í dag.1.json",
"data/unknown/Skíðasvæði opin um land allt.1.json",
"data/unknown/Skíðasvæði opin víða um land.1.json",
"data/unknown/Skíðasvæði opin.1.json",
"data/unknown/Skíðasvæði víða opin.1.json",
"data/unknown/Skíðasvæðin á Norðurlandi opin í dag.1.json",
"data/unknown/Skógareldar í Kaliforníu.1.json",
"data/unknown/Skúta strandaði í Skerjafirði.1.json",
"data/unknown/Slapp ómeiddur úr bílveltu.1.json",
"data/unknown/Slasaðist á torfæruhjóli.1.json",
"data/unknown/Slasaðist þegar fjórhjól valt.1.json",
"data/unknown/Slæm færð á Vestfjörðum.1.json",
"data/unknown/Snarpur skjálfti í Japan.1.json",
"data/unknown/Snjóflóðahætta á Tröllaskaga.1.json",
"data/unknown/Snjóþekja víða um land.1.json",
"data/unknown/Sótti veikan sjómann.1.json",
"data/unknown/Sprengdi sig í loft upp í mosku.1.json",
"data/unknown/Sprengdi sig í loft upp.1.json",
"data/unknown/Sprenging í Pakistan.1.json",
"data/unknown/Stúlkan fundin.1.json",
"data/unknown/Stúlkan komin í leitirnar.1.json",
"data/unknown/Stúlkan sem lýst var eftir fundin.1.json",
"data/unknown/Stútar stöðvaðir.1.json",
"data/unknown/Sumarbústaður brann til kaldra kola.1.json",
"data/unknown/Svörtu kassarnir fundnir.1.json",
"data/unknown/Sýknaður af ákæru um kynferðisbrot.1.json",
"data/unknown/Sýknaður af ákæru um líkamsárás.1.json",
"data/unknown/Sýknaður af sérstaklega hættulegri líkamsárás.1.json",
"data/unknown/Tala látinna hækkar enn.1.json",
"data/unknown/Tekinn dópaður undir stýri.1.json",
"data/unknown/Thelma valin Ljósberi ársins.1.json",
"data/unknown/Tilkynnt um tvö innbrot.1.json",
"data/unknown/Tíu gistu fangageymslur.1.json",
"data/unknown/Tveir á slysadeild eftir bílveltu.1.json",
"data/unknown/Tveir á slysadeild eftir harðan árekstur.1.json",
"data/unknown/Tveir fluttir á slysadeild eftir árekstur.1.json",
"data/unknown/Tveir úrskurðaðir í gæsluvarðhald.1.json",
"data/unknown/Tvö innbrot í borginni í nótt.1.json",
"data/unknown/Tvö innbrot í nótt.1.json",
"data/unknown/Umferðartafir á Suðurlandsvegi.1.json",
"data/unknown/Umsátrinu lokið.1.json",
"data/unknown/Ungur ökumaður lést.1.json",
"data/unknown/ÚPS.1.json",
"data/unknown/Úrskurðaður í fjögurra vikna gæsluvarðhald.1.json",
"data/unknown/Úrskurðaður í gæsluvarðhald.1.json",
"data/unknown/Útilokar ekki uppsagnir.1.json",
"data/unknown/Útskrifaður af gjörgæslu í dag.1.json",
"data/unknown/Útskrifuð af sjúkrahúsi.1.json",
"data/unknown/Varað við grjóthruni á Siglufjarðarvegi.1.json",
"data/unknown/Varað við hálku.1.json",
"data/unknown/Varað við hálkublettum.1.json",
"data/unknown/Varað við lúmskri hálku.1.json",
"data/unknown/Varað við stormi í kvöld.1.json",
"data/unknown/Verulega dregur úr umferð.1.json",
"data/unknown/Vilja Vaðlaheiðargöng.1.json",
"data/unknown/Vinnuslys í Kópavogi.1.json",
"data/unknown/Viðræðurnar halda áfram.1.json",
"data/unknown/Viðvörun frá Veðurstofu.1.json",
"data/unknown/Víða gott skíðafæri í dag.1.json",
"data/unknown/Víða hálka.1.json",
"data/unknown/Víða ófært.1.json",
"data/unknown/Vonast eftir niðurstöðu í dag.1.json",
"data/unknown/Vopnað rán í Mjóddinni.1.json",
"data/unknown/Þak sett á innheimtukostnað.1.json",
"data/unknown/Þing sett í dag.1.json",
"data/unknown/Þingkosningar í Ísrael í dag.1.json",
"data/unknown/Þjóðarsorg í Póllandi.1.json",
"data/unknown/Þokast í samkomulagsátt.1.json",
"data/unknown/Þrettán líkamsárásir um helgina.1.json",
"data/unknown/Þriggja bíla árekstur á Gullinbrú.1.json",
"data/unknown/Þriggja bíla árekstur á Miklubraut.1.json",
"data/unknown/Þriggja bíla árekstur í Ártúnsbrekkunni.1.json",
"data/unknown/Þrír á slysadeild eftir harðan árekstur.1.json",
"data/unknown/Þrír fluttir á sjúkrahús eftir árekstur.1.json",
"data/unknown/Þrír fluttir á sjúkrahús eftir bílveltu.1.json",
"data/unknown/Þrír fluttir á sjúkrahús eftir harðan árekstur.1.json",
"data/unknown/Þrír Palestínumenn drepnir.1.json",
"data/unknown/Þrír teknir fyrir ölvunarakstur.1.json",
"data/unknown/Þrír teknir undir áhrifum fíkniefna.1.json",
"data/unknown/Þrjú innbrot í nótt.1.json",
"data/unknown/Þungt hljóð í lögreglumönnum á suðurnesjum.1.json",
"data/unknown/Þúsundir mótmæla í Aþenu.1.json",
"data/unknown/Þyrla sótti meðvitundarlausa konu.1.json",
"data/unknown/Þyrla sótti veikan sjómann.1.json",
"data/unknown/Þyrlan sótti slasaðan sjómann.1.json",
"data/unknown/Þyrlan sótti veikan sjómann.1.json",
"data/unknown/Þyrlan sækir slasaðan vélsleðamann.1.json"]


def yield_files_with_ending(ending, author):
    for root, dirs, files in os.walk(DATADIR.format(author)):
        for file in files:
            if file.endswith(ending):
                yield(os.path.join(root, file))


def clean_items(item):
    temp = {}
    for k, v in item.items():
        temp[k.strip()] = v.strip()
    return temp


def add_category_to_json():
    for author in authors:
        print "Doing {}".format(DATADIR.format(author))
        for jsonfile in yield_files_with_ending(".json", author):
            with open(jsonfile, "r") as f:
                data = json.loads(f.read())
                # clean the line endings
                for k, v in data.items():
                    data[k] = clean_item(v)
                # Get the category
                #gzip_file = os.path.join(os.path.splitext.splitext(jsonfile)[0],os.path.splitext(jsonfile)[1].replace('json', "gz"))
                gzip_file = jsonfile.replace(".json", ".html.gz")
                try:
                    with gzip.open(gzip_file, "rb") as fgz:
                        soup = BeautifulSoup(fgz.read(), "lxml", from_encoding="iso-8859-1")
                        category = soup.find(class_="source-t FRETTIR-cat")
                        data['category'] = category.text.strip()
                except:
                    print "ERROR in {}".format(jsonfile)
            with open(jsonfile, "w") as f:
                f.write(json.dumps(data))


def add_category_to_json_duplicates():
    for jsonfile in DUPLICATES:
        with open(jsonfile, "r") as f:
            data = json.loads(f.read())
            try:
                print "Category {} in {}".format(data['category'], jsonfile)
            except KeyError:
                for k, v in data.items():
                    data[k] = clean_item(v)
                data['category'] = "Innlent"
        with open(jsonfile, "w") as f:
                f.write(json.dumps(data))


def yield_sourcefiles(ending="gz"):
    for root, dirs, files in os.walk("visir_slurper/data"):
        for file in files:
            if file.endswith(ending):
                filename = os.path.join(root, file)
                done_filename = filename.replace("data", "data_reparse").replace("-html.gz", ".json")
                if os.path.isfile(done_filename):
                    print "Already done %s" % done_filename
                    os.remove(filename)
                    os.remove(filename.replace("-html.gz", ".json"))
                    os.remove(filename.replace("-html.gz", ".txt"))
                else:
                    yield(os.path.join(root, file))


def text_with_newlines(elem):
        """
        Extract text from an element converting br to newlines
        """
        text = ""
        for e in elem.recursiveChildGenerator():
            if isinstance(e, basestring):
                text += e
            elif e.name == "br":
                text += "\n"
        return "\n".join([x for x in text.splitlines() if x.strip()])


def save_json_and_text(item):
        date_parsed = parser.parse(item["date_published"])
        directory = os.path.join(REPARSE_SAVE_DIR,
                                 date_parsed.strftime("%Y"),
                                 date_parsed.strftime("%m"),
                                 date_parsed.strftime("%d")
                                 )
        json_filename = os.path.join(directory, item["id"] + ".json")
        txt_filename = os.path.join(directory, item["id"] + ".txt")
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(txt_filename, "w") as f:
            f.write(item["article_text"].encode("utf-8"))
        # store the article_text
        article_text = item["article_text"]
        # pop article text from the item so as to no write it to the json
        item.pop("article_text", None)
        with open(json_filename, "w") as f:
            f.write(json.dumps(item))
        print "  Saved json: %s" % json_filename


def save_author(item):
        author = item['author']
        filename = author.replace(" ", "_") + ".csv"
        directory = os.path.join(REPARSE_SAVE_DIR,
                                 "authors")
        filename = os.path.join(directory, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if os.path.exists(filename):
            with open(filename, "ab") as f:
                f.write(item["id"] + "\n")
        else:
            with open(filename, "wb") as f:
                f.write(item["author"].encode("utf-8") + "\n")
                f.write(item["id"] + "\n")
        print "  Saved author: %s" % author


def reparse_for_authors():
    for filename in yield_sourcefiles():
        print "Parsing %s" % filename
        with gzip.open(filename) as f:
            html = f.read()
            html = html.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        [s.extract() for s in soup("script")]
        item = {}
        #id = response.url.split("/")[-1:][0]
        id = filename.split("-")[0].split("/")[-1:][0]
        item["id"] = id
        url = soup.find(attrs={"rel": "canonical"})["href"]
        item["url"] = url
        try:
            date_published = soup.find(attrs={"itemprop": "datePublished"})["content"]
            headline = soup.find(attrs={"itemprop": "headline"}).text
        except (AttributeError, TypeError):
            # Don"t care about articles without dates or headlines
            return
        description = soup.find(attrs={"itemprop": "description"})["content"]
        default_author = u"unknown"
        default_possible_authors = ""

        try:
            # Multiple authors is messed up in visir.is markup
            # This handles that
            author = soup.find_all(attrs={"itemprop": "author"})
            if author:
                author = " og ".join([x.text.strip() for x in author]).strip()
            else:
                author = default_author
        except AttributeError:
            # If no author then assign 'unknown'
            author = default_author
        possible_authors = soup.find(class_="meta")
        if possible_authors is not None:
            possible_authors = possible_authors.text.strip()
        else:
            possible_authors = default_possible_authors
        category = soup.find(class_=re.compile("source-t")).text

        # drop cruft
        crufts = ["meta",
                  "mob-share",
                  "imgtext",
                  "fb-post",
                  "twitter-tweet",
                  "art-embed"
                  ]
        for k in crufts:
            tags = soup.find_all(class_=k)
            for tag in tags:
                tag.extract()
        # Extract the text
        text = soup.find(attrs={"itemprop": "articleBody"})
        text = text_with_newlines(text)
        text = headline + "\n" + description + "\n" + text
        item["date_published"] = date_published
        item["headline"] = headline
        item["author"] = author
        item["possible_authors"] = possible_authors
        item["article_text"] = text
        item["description"] = description
        item['category'] = category
        #item["body"] = html
        # strip
        item = clean_items(item)
        save_json_and_text(item)
        save_author(item)


if __name__ == '__main__':
    reparse_for_authors()
