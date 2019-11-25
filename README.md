# Microchip Atmel SAMR34/35 platform for PlatformIO

 **Version 0.0.9** ( [look here, if there is something new](https://github.com/Wiz-IO/platform-sam-lora/wiki/VERSION) )
* OS Windows **( for now )** 
* * Baremetal 
* * Arduino ( in process... )
* Board [Microchip SAM R34 Xplained Pro](https://www.microchip.com/DevelopmentTools/ProductDetails/dm320111)
* [Framework Source Codes and Examples](https://github.com/Wiz-IO/framework-sam-lora)
* [Wiki ( read )](https://github.com/Wiz-IO/platform-sam-lora/wiki)

The project is in process and is very beta version - **may be bugs** 

## Baremetal
* CMSIS
* [ASF ( v 3.47.0.96 )](https://github.com/Wiz-IO/platform-sam-lora/wiki/ASF)
* [Blink](https://github.com/Wiz-IO/framework-sam-lora/tree/master/examples/asf_blink)

## Arduino Core
* Arduino core
* GPIO, Serial, I2C, SPI
* Variant: Microchip SAM R34 Xplained Pro
* [Hello World](https://github.com/Wiz-IO/framework-sam-lora/blob/master/examples/arduino_hello_world/)
* [OLED from the screenshot](https://github.com/Wiz-IO/framework-sam-lora/tree/master/examples/arduino_oled_i2c)

![sam](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/sam34-oled.jpg)

[The first steps - youtube](https://www.youtube.com/watch?v=Bhc3n0Go5KI)

[Simple LoRa](https://www.youtube.com/watch?v=3bJiQ3b2fgA)

## Platform Installation

Install VS Code + PlatformIO

PlatformIO - Home - Platforms - Advanced Installation

Paste link: https://github.com/Wiz-IO/platform-sam-lora

## Fast Uninstal
* goto C:\Users\USER_NAME\.platformio\platforms **delete** folder **sam-lora** ( builders )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **framework-sam-lora** ( sources )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **tool-sam-lora** ( uploader )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **toolchain-gccarmnoneeabi** (compiler )

![sam](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/sam.png)

## Baremetal INI
```ini
[env:samr34xpro]
platform = sam-lora
board = samr34xpro
framework = baremetal
monitor_port = COMx     
monitor_speed = 115200  
```

## Arduino INI
```ini
[env:samr34xpro]
platform = sam-lora
board = samr34xpro
framework = arduino
monitor_port = COMx     
monitor_speed = 115200  
```

## Road Map
* Baremetal Uploaders ( now work with atbackend/atprogram )
* Baremetal ASF/CMSIS
* Arduino Bootloader
* Arduino Core
* Arduino Libraries
* Examples

## Thanks to

* [Ivan Kravets ( PlatformIO )](https://platformio.org/)
* [Comet Electronics](https://www.comet.bg/en/)

>If you want to help / support:   
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ESUP9LCZMZTD6)
