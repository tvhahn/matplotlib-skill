
## v2base  (207 runs)

| model | runs | chart | turn cap | timeout | $/run | s/run | routed | exemplars read | reviewed | ERROR | WARN | STYLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | 69 | 66 | 0 | 0 | 0.143 | 78 | 46/69 | 0/69 | 0/69 | 0 | 16 | 6 |
| claude-opus-5-5 | 69 | 69 | 0 | 0 | 0.335 | 52 | 48/69 | 0/69 | 0/69 | 0 | 21 | 0 |
| claude-sonnet-5-5 | 69 | 69 | 0 | 0 | 0.162 | 41 | 51/69 | 0/69 | 0/69 | 0 | 21 | 0 |
| ALL | 207 | 204 | 0 | 0 | 0.213 | 57 | 145/207 | 0/207 | 0/207 | 0 | 58 | 6 |

Misrouted (prompt: runs): n-confusion-wine: 9, n-dumbbell-healthexp: 9, n-ecdf-taxis: 9, n-mix-iowa: 9, n-slope-gapminder: 9, n-training-cancer: 9, n-ridgeline-seattle: 4, m-function-happiness: 3, x-titanic-grouped: 1
Checker findings by code: low-contrast-text 19, footer 19, annotation-on-data 14, text-colour 6, fractional-ticks 4, legend-on-data 2

## v3  (207 runs)

| model | runs | chart | turn cap | timeout | $/run | s/run | routed | exemplars read | reviewed | ERROR | WARN | STYLE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | 69 | 67 | 1 | 0 | 0.258 | 169 | 67/69 | 67/69 | 67/69 | 0 | 0 | 0 |
| claude-opus-5-5 | 69 | 69 | 0 | 0 | 0.588 | 94 | 69/69 | 69/69 | 69/69 | 0 | 4 | 1 |
| claude-sonnet-5-5 | 69 | 69 | 0 | 0 | 0.228 | 55 | 69/69 | 60/69 | 48/69 | 0 | 0 | 0 |
| ALL | 207 | 205 | 1 | 0 | 0.358 | 106 | 205/207 | 196/207 | 184/207 | 0 | 4 | 1 |

Misrouted (prompt: runs): m-function-happiness: 2
Checker findings by code: footer 3, text-colour 1, annotation-on-data 1
