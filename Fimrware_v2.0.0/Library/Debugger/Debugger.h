
#include <Arduino.h>

template <typename T>  
void Debugger(byte index, T data){    
 Serial.print("#");    
 Serial.print(index);    
 String str = String(data); // Converte o valor em string    
 Serial.println(str);    
 delay(50);  

 // Aguarda retorno se break
    if (str == "BREAK") {
        while (true) {
            if (Serial.available()) {
                if (Serial.read() == '#') {
                    break;
                }
            }
            delay(50);
        }
        str = "";
    }
}  


