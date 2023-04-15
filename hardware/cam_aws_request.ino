#include "WiFi.h"
#include "esp_camera.h"
#include "Arduino.h"
#include "soc/soc.h"           
#include "soc/rtc_cntl_reg.h"  
#include "driver/rtc_io.h"
#include <FS.h>
#include <HTTPClient.h>
#include "esp_http_client.h"
#include "Base64.h"
#include "mbedtls/base64.h"
#include <NTPClient.h>
#include <WiFiUdp.h>

// OV2640 camera module pins (CAMERA_MODEL_AI_THINKER)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char* ssid = "Pikachu-5G";
const char* password = "LambdaFunction2022!";

const char* s3_endpoint = "s3.amazonaws.com";
const char* s3_bucket = "rideshield-img";
const char* s3_region = "us-east-2";

void take_save_photo( void ) {
    camera_fb_t * fb = NULL; 
    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Failed");
        return;
    }
    
    HTTPClient http;

    // Set the destination URL for the PUT request
    http.begin("http://rideshield.s3.us-east-2.amazonaws.com/ligma.jpeg");
  
    // Set the content type header for the request
    http.addHeader("Content-Type", "image/jpeg");
  
    // Set the body of the request (the data you want to send)
    //String requestBody = "This is the data I want to send";
    //http.addHeader("Content-Length", String(requestBody.length())); // Set the content length header
    int httpResponseCode = http.sendRequest("PUT", (uint8_t*)fb->buf, fb->len); // Send the PUT request and get the HTTP response code
    Serial.println(http.getString());
  
    // Check the response code to see if the request was successful
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    }
    else {
      Serial.println("Error sending PUT request");
    }
  
    // Disconnect from the server
    http.end();
    
    // Free memory allocated for photo buffer
    esp_camera_fb_return(fb);
}

void setup() {
    Serial.begin(9600);
  
    //Connect to wifi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting to WiFi...");
      Serial.println(WiFi.status());
    }
    Serial.println("Connected to WiFi");

    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

    // initialize OV2640 camera module
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        ESP.restart();
    } 
}

void loop() {
    take_save_photo();
    Serial.printf("Took Photo");
    delay (5000); //Wait 5 sec
}