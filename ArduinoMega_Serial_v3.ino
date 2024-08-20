//Arduino Mega utiliza los Serial1, Serial2, y Serial3
const int Led_cmd=7;
void setup()
{
  Serial.begin(57600);
  Serial3.begin(57600);

  pinMode(Led_cmd, OUTPUT);
  Serial.println("Iniciando.......");
  delay(2000);


}
int interval=200;
long previous_millis=0;


int pot;
String msg="";
float valor,valor3;
String readString="";
String payloadBroker="";

char inicio=2;
char final=4;

void loop() {
    
   
    //-----------READ SERIAL DATA---------------
        
          if(Serial3.available()){
            payloadBroker=Serial3.readStringUntil('\n');
          }
         
    //----END READING------------------



  //--Data potenciometro
  pot =analogRead(A0);
  valor=pot/15.0;
  valor3=valor*5.0;
  
  

     if ((millis() - previous_millis) > interval) {
        previous_millis = millis();
        
        //--Enviar Data
        msg.concat(pot);//
        msg.concat(",");
        msg.concat(valor);
        msg.concat(",");
        msg.concat(valor3);
        //--DATA ENVIADA-----
        Serial3.println(msg);//usar solo print y no println para no tener un salto de linea.
        //--FIN ENVIAR DATA---
        Serial.print("Enviada:");
        Serial.print(msg);
        msg = "";//limpiar data
    
        int t=payloadBroker.length();//obtiene el tamaño.  
        payloadBroker.remove(t-1,1);//elimina el ultimo caracter salto de linea.

        Serial.print("; Recibida:");
        Serial.print(payloadBroker);
        Serial.print(", tamaño=");
        Serial.println(payloadBroker.length());
             
      }
    
    

    if(payloadBroker=="ledOff"){

      digitalWrite(Led_cmd, LOW);
      //Serial.println("cmd=ledOff");

    }else if(payloadBroker=="ledOn"){
      digitalWrite(Led_cmd, HIGH);
      //Serial.println("cmd=ledOn");
     }

  
}