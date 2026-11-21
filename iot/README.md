# IoT — ESP32 e Wokwi

Código-fonte do monitor experimental de nível de água e chuva, incluindo `src/main.cpp`, `referencia/sketch.ino`, `diagram.json` e `platformio.ini`. As medições e os alertas apresentados são simulações, não leituras em campo nem um serviço de emergência.

A arquitetura AWS `S3 → Lambda → RDS` foi validada com eventos JSON; a conexão automática entre o ESP32 físico e a nuvem não foi comprovada. Consulte `../docs/IMPLEMENTACAO_AWS.md`.
