# AVIVA IoT - circuito reparado para VS Code / PlatformIO / Wokwi

**Objetivo**: simular a classificacao NORMAL, ATENCAO e CRITICO para demonstracao academica. Nao e monitoramento real, nao substitui Defesa Civil.

## Problemas da versao anterior

- O simulador mostrou `FALHA_SENSOR_NIVEL`: ausencia de eco valido no HC-SR04. A captura indicava o pino ECHO sem fio visivel.
- O log mostrou `LEDC is not initialized`: o uso de `tone()`/`noTone()` nao estava confiavel neste firmware.
- O circuito anterior tinha rotas complexas de resistores que atrapalhavam a verificacao visual.

## Corrigido nesta versao

1. Novo `diagram.json` simplificado: TRIG -> GPIO5 (verde), ECHO -> GPIO18 (azul), potenciometro -> GPIO34 (laranja), DHT22 -> GPIO4 (violeta), LEDs -> GPIO23/22/21, buzzer -> GPIO19.
2. O codigo agora usa pulso digital para o buzzer (sem LEDC), apenas para demonstracao no simulador.
3. Ao ocorrer falha do HC-SR04, o serial informa `SEM_ECHO` para diagnostico.
4. Resistor dos LEDs foi retirado **apenas do desenho da simulacao**; em hardware fisico coloque resistores de 220–330 ohms em serie com LEDs. No circuito real use divisor de tensao ou conversor de nivel no ECHO de 5 V para proteger o GPIO 3,3 V do ESP32.

## Passo a passo

1. Feche o Wokwi antigo (Stop) e no VS Code use File -> Open Folder nesta pasta, que contem `platformio.ini` na raiz. **Nao misture arquivos de projetos de versoes diferentes**.
2. Abra o terminal do PlatformIO pelo comando `PlatformIO: Open PlatformIO Core CLI`.
3. Execute `pio run` para recompilar o **main.cpp atualizado**, gerando novo firmware.
4. `Ctrl+Shift+P` -> `Wokwi: Start Simulator`. Abra o Wokwi Terminal.
5. Teste HC-SR04 clicando nele e escolhendo distancia 250 cm, 170 cm e 90 cm. Ajuste o potenciometro proximo do minimo para simular chuva baixa (essa e uma entrada sintetica, nao um sensor de chuva real).
6. Espere ~2 segundos por leitura. Confira colunas da saida `AVIVA_IOT;tempo;nivel;chuva;umidade;classificacao;qualidade`.

| Distancia ultrassonico | Nivel deduzido | Chuva simulada baixa | Esperado |
|---|---|---|---|
| 250 cm | 50 cm | < 25 mm/h | NORMAL |
| 170 cm | 130 cm | < 25 mm/h | ATENCAO |
| 90 cm | 210 cm | < 25 mm/h | CRITICO |

Se o serial continuar com `SEM_ECHO`, confirme visualmente a existencia do **fio azul** entre `nivel:ECHO` e `esp:D18`, e que o simulador foi reiniciado na pasta correta. Se mostrar `FALHA_SENSOR_DHT22`, confira fio violeta `umidade:SDA` -> `esp:D4`.

**Status de verificacao:** ligacoes e codigo auditados estaticamente; a compilacao do firmware e a execucao do Wokwi precisam ser confirmadas no seu computador.
