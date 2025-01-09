/*
  Data: 09/01/2025
  Autor: DALÇÓQUIO AUTOMAÇÃO
  Exemplo: Leitura dos valores de variáveis com App Debuger em Visual Basic
 
*/

#include <Debuger.h>

// Use agora: Debuger(index, data);

// Se preferir use este comando direto sem uso da library:
// Serial.println("#Index" + Variável); delay(50); // recomendado um delay 

void setup() {
  Serial.begin(9600);

  while(!Serial) {
        ; // aguarda conexão serial
  }
    
  pinMode(13, OUTPUT);
  
}

void loop() {
    digitalWrite(13, HIGH);
    Debuger(1, 1);
    delay(500);

    digitalWrite(13, LOW);
    Debuger(1, 0);
    delay(500);
    
    Debuger(2, millis());

}
