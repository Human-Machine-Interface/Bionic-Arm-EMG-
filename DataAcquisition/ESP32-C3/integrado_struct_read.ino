
#include "FS.h"
#include "SD.h"
#include "SPI.h"

#define CHAR_SIZE 23

File root;
File dataFile;

const int chipSelect = 4;

bool flag = true;
struct emg_data {
    uint16_t  mw1;
    uint16_t  mw2;
    uint16_t  mw3;
    float     ax;
    float     ay;
    float     az;
    float     gx;
    float     gy;
    float     gz;
};
emg_data emg_array[5000];
void setup() {
    Serial.begin(115200);
    Serial.print("Initializing SD card...");

    if (!SD.begin(1)) {
        Serial.println("Card failed, or not present");
        return;
    }

    Serial.println("card initialized.");
    dataFile = SD.open("/Task3/S3.1_R1.dat", FILE_READ);
    
    root = SD.open("/DAT");
    printDirectoryMain(root);
    Serial.println("DONE");
    
}

void loop() {
  /*if(flag){
    Serial.print("FLAG");
    if (dataFile.available()) {
        //struct emg_data myData;
        Serial.print("FILE AVAILABLE");
        dataFile.read((uint8_t *)&emg_array, sizeof(emg_array));
        for (int i = 0; i < 5000; i++) {
          Serial.print(emg_array[i].mw1);
          Serial.print(",");
          Serial.print(emg_array[i].mw2);
          Serial.print(",");
          Serial.print(emg_array[i].mw3);
          Serial.print(",");
          Serial.print(emg_array[i].ax);
          Serial.print(",");
          Serial.print(emg_array[i].ay);
          Serial.print(",");
          Serial.print(emg_array[i].az);
          Serial.print(",");
          Serial.print(emg_array[i].gx);
          Serial.print(",");
          Serial.print(emg_array[i].gy);
          Serial.print(",");
          Serial.println(emg_array[i].gz);
          
        }
        flag = false;
        delay(50);
    }
  }*/
}

void removeDir(fs::FS &fs, const char * path){
    Serial.printf("Removing Dir: %s\n", path);
    if(fs.rmdir(path)){
        Serial.println("Dir removed");
    } else {
        Serial.println("rmdir failed");
    }
}

void printDirectoryMain(File dir) {

  while (true) {
    File entry =  dir.openNextFile();
    if (! entry) {
      Serial.println("OUT_MAIN");
      // no more files
      break;
    }
    if (entry.isDirectory()) {
      char file_name[CHAR_SIZE] = "/";
      strcat(file_name, dir.name());
      strcat(file_name, "/");
      strcat(file_name, entry.name());
      Serial.println(file_name);
      root = SD.open(file_name); 
      printDirectoryTask(root, file_name);
    }
    entry.close();
  }
}


void printDirectoryTask(File dir, char file[CHAR_SIZE]) {
  
  while (true) {
    //Serial.println("HEY");
    //Serial.println(dir.name());
    File entry_task = dir.openNextFile();
    if (! entry_task) {
      // no more files
      Serial.println("OUT_task");
      break;
    }
    char file_name[CHAR_SIZE] = "";
    memcpy(file_name, file, sizeof(file[0])*CHAR_SIZE);
    strcat(file_name, "/");
    strcat(file_name, entry_task.name());
    //Serial.println(file_name);
    File file_dat = SD.open(file_name, FILE_READ);
    int file_size = strlen(entry_task.name());
      file_name[1]  = 'T';
      file_name[2]  = 'X';
      file_name[3]  = 'T';
      
    if (file_size == 11){
      file_name[19] = 't';
      file_name[20] = 'x';
      file_name[21] = 't';
      }else{
        file_name[20] = 't';
        file_name[21] = 'x';
        file_name[22] = 't';
        }
    
    Serial.println(file_name);
    entry_task.close();
    file_dat.read((uint8_t *)&emg_array, sizeof(emg_array));
    delay(100);
    file_dat.close();
    
    File file_txt = SD.open(file_name, FILE_WRITE);
    for (int i = 0; i < 5000; i++) {
          file_txt.print(emg_array[i].mw1);
          file_txt.print(",");
          file_txt.print(emg_array[i].mw2);
          file_txt.print(",");
          file_txt.print(emg_array[i].mw3);
          file_txt.print(",");
          file_txt.print(emg_array[i].ax);
          file_txt.print(",");
          file_txt.print(emg_array[i].ay);
          file_txt.print(",");
          file_txt.print(emg_array[i].az);
          file_txt.print(",");
          file_txt.print(emg_array[i].gx);
          file_txt.print(",");
          file_txt.print(emg_array[i].gy);
          file_txt.print(",");
          file_txt.println(emg_array[i].gz); 
        }
     file_txt.close();
     delay(1000);
    }
}
