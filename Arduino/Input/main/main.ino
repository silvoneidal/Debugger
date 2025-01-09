/*
  Data: 23/12/2024
  Autor: DALÇÓQUIO AUTOMAÇÃO
  Exemplo: Leitura dos valores de variáveis com App Debugger.exe em Visual Basic
 
*/

bool input; // variável para status da entrada digital

// Use esta strutura em seu sketch para um comando mais simplificado
struct Debug{
  template <typename T>
  void print(byte index, T data){
    Serial.print("#");
    Serial.print(index);
    String str = String(data); // Converte o valor em string
    Serial.println(str);
    delay(50);
  }
  
}debug;

// Use agora: debug.print(index, data);

// Se preferir use este comando direto sem uso da strutura:
// Serial.println("#Index" + Variável); delay(50); // recomendado um delay 

void setup() {
  Serial.begin(9600);

  while(!Serial) {
        ; // aguarda conexão serial
  }
    
  pinMode(8, INPUT_PULLUP);
  
}

void loop() {
    if(digitalRead(8)){
        input = 1;
        debug.print(1,1);
    }else{
        input = 0;
        debug.print(1, 0);
    }

}