
#include <Arduino.h>

template <typename T>  
void Debugger(byte index, T data){    
 Serial.print("#");    
 Serial.print(index);    
 String str = String(data); // Converte o valor em string    
 Serial.println(str);    
 delay(50);  
}  


