# Snabbt exempel på frekvensbaserat nät
Utgått från _Mandl_Visum.ver_.
Gjort om den till frekvensbaserad.
Exporterat till _Mandl_Visum_headway.net_. Då har jag valt ut vilka tabeller som bör vara med.

Sedan har jag gått in och kommenterat direkt i filen.
Men jag har bara kommenterat det som skiljer från förut.

I Visumfilen så har jag skapat ett attribut _Headway_ som jag har lagt på nivån _Line route_.

Traditionellt brukar man lägga den variabeln på nivån _Time profile_. Men så länge vi bara har en time profile för vardera line route så spelar det ingen roll. Halmstadsnätverket har lagt sin variabel för vardera line route, så då gjorde jag likadant.

Sedan så misstänker jag att ditt skript som räknar ut score inte fungerar som tänkt längre. Den frekvensbaserade utläggningen skriver JRT till en annan skim matris tex. Men jag har inte kollat det. 

