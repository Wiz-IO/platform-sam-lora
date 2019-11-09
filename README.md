# Microchip Atmel ATSAM3x platform for PlatformIO

 **Version 0.0.1** ( look here, if there is something new )
* OS Windows **( for now )** 
* * Baremetal
* * Arduino ( in process )
* BOARD [Microchip SAM R34 Xplained Pro](https://www.microchip.com/DevelopmentTools/ProductDetails/dm320111)

The project is in process and is very beta version - **may be bugs** 


## Platform Installation

_( **work only baremetal part** )_

Install VS Code + PlatformIO

PlatformIO - Home - Platforms - Advanced Installation

Paste link: https://github.com/Wiz-IO/platform-sam-lora

## Fast Uninstal
* goto C:\Users\USER_NAME\.platformio\platforms **delete** folder **sam-lora** ( builders )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **framework-sam-lora** ( sources )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **tool-sam-lora** ( uploader )
* goto C:\Users\USER_NAME\.platformio\packages **delete** folder **toolchain-gccarmnoneeabi** (compiler )

![sam](https://raw.githubusercontent.com/Wiz-IO/LIB/master/images/sam.png)

## Road Map
* Baremetal Uploaders ( now work with atbackend/atprogram )
* Baremetal ASF/CMSIS
* Arduino Bootloader
* Arduino Core
* Arduino Libraries
* Examples


>If you want to help / support:   
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ESUP9LCZMZTD6)
