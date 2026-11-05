# Jev og Laya: demo

Et live «kundeservice-race»: [Laya](https://huggingface.co/convaiinnovations/laya), en åpen
System 1-beslutningsmodell som er kompatibel med TypeSafes Jev-API, mot to lokale språkmodeller i
Ollama. Hver kundehenvendelse får tre typede spørsmål: hvilken avdeling (choice), hvor mye det haster
(score 0–3) og om kunden vil ha pengene tilbake (ja/nei).

Presentasjonen ligger i [presentation/jev-laya.html](presentation/jev-laya.html). Serv mappen med
`python3 -m http.server 8765` fra `presentation/`, åpne `http://localhost:8765/jev-laya.html` og trykk
`S` for talenotater.

Kjørerekkefølge for en Lunch &amp; Learn på 15–20 minutter: forside, System 1 vs. System 2, og «Møt Jev
og Laya» (slide 3), som forklarer racet. Bytt deretter til terminalen og kjør demoen. Kom tilbake til
«Hva skjedde akkurat?» (slide 4) og fortsett derfra.

## Oppsett

Krever en Mac med Apple Silicon, [uv](https://docs.astral.sh/uv/) og [Ollama](https://ollama.com).

```bash
uv sync
ollama pull mistral:latest
ollama pull gemma:2b
uv run jev-laya-demo --tickets 1 --repeats 0 --quality-only --no-pause   # første kjøring laster ned Laya (~1,5 GB)
```

Etter første nedlasting kjører demoen helt offline (`HF_HUB_OFFLINE` settes automatisk når
modellen ligger i cachen).

## Kjør demoen

```bash
uv run jev-laya-demo
```

Demoen laster Laya og varmer opp alle modellene før racet, så ingen betaler for kaldstart. Den viser
en kort forklaring av de tre spørsmålene og venter på Enter. Under racet viser hver kolonne antall
saker ferdig, tid brukt og antall output-tokens skrevet. Etterpå kommer fem resultattabeller med
forklaring under hver: hastighet, kvalitet, Layas sikkerhet på de vriene sakene, om svarene endrer
seg ved ny kjøring, og hva en million saker om dagen ville kostet. Trykk Enter mellom hver tabell.

Hele kjøringen tar rundt 2–3 minutter på en M-serie Mac med 12 saker. Bruk et bredt terminalvindu
(140+ kolonner).

| flagg | standard | effekt |
| --- | --- | --- |
| `--tickets N` | 12 | antall saker i racet (maks 20) |
| `--models a,b` | `mistral:latest,gemma:2b` | Ollama-modellene som deltar |
| `--single-call` | av | språkmodellene får alle tre spørsmål i ett kall i stedet for ett kall per spørsmål |
| `--no-reason` | av | språkmodellene svarer kun med JSON, uten én setning begrunnelse først |
| `--repeats N` | 3 | omkjøringer av de 7 vriene sakene for konsistenssjekken (0 hopper over) |
| `--temperature T` | 0.7 | temperatur for språkmodellene |
| `--quality-only` | av | hopp over live-racet |
| `--no-pause` | av | vis alle tabeller uten å vente på Enter |

## Hva er (og er ikke) rettferdig

Som standard gjør språkmodellene ett kall per spørsmål og skriver en kort begrunnelse før JSON-en.
Det er det vanlige mønsteret «tenk først, så strukturert svar», men det koster output-tokens. Laya er
forhåndslastet, varmet opp og kjører i batch. For å gi språkmodellene deres raskeste oppsett, kjør
`uv run jev-laya-demo --single-call --no-reason`. Språkmodellene kaldstartes ikke: alle modeller er
varme før racet starter.

Treffsikkerhet måles mot håndskrevne fasitsvar i `src/jev_laya_demo/tickets.py`. Et ugyldig svar
teller som feil, og hastegrad regnes som riktig innenfor ett nivå fra fasit. En typisk kjøring
(M-serie, alle 20 saker):

| | tid | per sak | output-tokens | gyldige svar | riktig totalt | endret svar over 3 omkjøringer |
| --- | --- | --- | --- | --- | --- | --- |
| Laya | 1,0 s | 50 ms | 0 | 100 % | 90 % | 0 / 21 |
| Mistral 7B | 57 s | 2,8 s | 2 199 | 100 % | 93 % | 4 / 21 |
| Gemma 2B | 45 s | 2,3 s | 2 790 | 90 % | 68 % | 12 / 21 |

Med standard 12 saker ga en prøvekjøring 94 % riktig for Laya, 92 % for Mistral og 67 % for Gemma.

Grunnmodellen til Laya ligger noen få prosentpoeng fra Mistral totalt (Mistral varierer fra kjøring
til kjøring), og svakest er den på avdelingsruting. Det stemmer med modellkortet: grunnmodellene er et
utgangspunkt for finjustering, ikke et orakel uten trening.
